from .models import Post, PostReactions, Comment, CommentReactions
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.db.models import Count, F, Q
from django.core.exceptions import SuspiciousOperation
from django.db.models import Prefetch


def getUserData(user):
    return {"user_id": user.pk, "name": user.userName, "profile_pic_url": user.userPhoto}


def getReactions(reactions):
    reactionTypes = []
    for reaction in reactions:
        reactionTypes.append(reaction['reactionType'])
    return reactionTypes

def getCommentData(comment, commentReactions):
    comment_data = {}
    comment_data["comment_id"] = comment['id']
    comment_data["commenter"] = {"user_id": comment["user"], "name": comment["user__userName"], "profile_pic_url": comment["user__userPhoto"]}
    comment_data["commented_at"] = comment['commentedTime'].strftime('%y-%m-%d %H:%M:%S.%f')
    comment_data["comment_content"] = comment['commentText']
    comment_data["reactions"] = get_reaction_object(commentReactions)
    return comment_data


def getReplyData(comment):
    commentData = {}
    commentData["comment_id"] = comment.pk
    commenter = getUserData(comment.user)
    commentData["commenter"] = commenter
    commentData["commented_at"] = comment.commentedTime.strftime('%y-%m-%d %H:%M:%S.%f')
    commentData["comment_content"] = comment.commentText
    return commentData

def get_reaction_object(reaction_dic):
    return {"count": reaction_dic["count"], "type": list(reaction_dic["type"])}

def get_post_content(post):

    postData = {}

    commentOfPost = Comment.objects.select_related('user').filter(post=post, commented_on=None).values('id', 'commented_on', 'user', 'user__userName', 'user__userPhoto', 'commentText', 'commentedTime')

    comment_ids = []
    for comment in commentOfPost:
        comment_ids.append(comment['id'])


    postReactions = PostReactions.objects.filter(post=post).values_list('reactionType', flat=True)

    count = len(postReactions)
    reactionTypes = list(set(postReactions))

    all_comment_replys = Comment.objects.select_related('user').filter(commented_on__in=comment_ids).values('id', 'commented_on', 'user', 'user__userName', 'user__userPhoto', 'commentText', 'commentedTime')

    for comment in all_comment_replys:
        comment_ids.append(comment['id'])

    all_reply_reactions = CommentReactions.objects.filter(comment_id__in=comment_ids).values('comment_id', 'reactionType')

    comment_replys = {}
    for reply in all_comment_replys:
        try:
            comment_replys[reply['commented_on']].append(reply)
        except KeyError:
            comment_replys[reply['commented_on']] = [reply]

    comment_reactions = {}
    for reaction in all_reply_reactions:
        try:
            reply = comment_reactions[reaction['comment_id']]
            reply['count'] += 1
            reply['type'].add(reaction['reactionType'])
        except:
            comment_reactions[reaction['comment_id']] = {"count": 1, "type": set([reaction['reactionType']])}

    commentsArray = []
    for comment in commentOfPost:
        comment_data = getCommentData(comment, comment_reactions[comment['id']])
        replyArray = []
        for reply in comment_replys[comment['id']]:
            try:
                replyReactions = comment_reactions[reply['id']]
            except KeyError:
                replyReactions = {"count": 0, "type": []}
            replyArray.append(getCommentData(reply, replyReactions))
        comment_data["replies_count"] = len(replyArray)
        comment_data["replies"] = replyArray
        commentsArray.append(comment_data)

    postData["post_id"] = post.pk
    postData["posted_by"] = getUserData(post.user)
    postData["posted_at"] = post.postedTime.strftime('%y-%m-%d %H:%M:%S.%f')
    postData["post_content"] = post.postBody
    postData["reactions"] = {"count": count, "type": reactionTypes}
    postData["comments"] = commentsArray
    postData["comments_count"] = len(commentsArray)
    return postData


def get_post(post_id):
    post = Post.objects.select_related('user').get(pk=post_id)
    return get_post_content(post)


def create_post(user_id, post_content):
    post = Post(user_id=user_id, postBody=post_content, postedTime=datetime.datetime.now())
    post.save()
    return post.pk


def add_comment(post_id, comment_user_id, comment_text):
    comment = Comment(post_id=post_id, commented_on=None, user_id=comment_user_id, commentText=comment_text, commentedTime=datetime.datetime.now())
    comment.save()
    return comment.pk


def reply_to_comment(comment_id, reply_user_id, reply_text):
    comment = Comment.objects.select_related('user', 'post').get(pk=comment_id)
    comment_on_id = comment.commented_on
    if comment_on_id is not None:
        comment = Comment.objects.select_related('user', 'post').get(id=comment.commented_on.id)
    reply = Comment(post=comment.post, commented_on=comment, user_id=reply_user_id, commentText=reply_text, commentedTime=datetime.datetime.now())
    reply.save()
    return reply.pk


def react_to_post(user_id, post_id, reaction_type):
    try:
        post_like = PostReactions.objects.get(post_id=post_id, user_id=user_id)
        if post_like.reactionType == reaction_type:
            post_like.delete()
        else:
            post_like.reactionType = reaction_type
            post_like.save()
    except ObjectDoesNotExist:
        post_like = PostReactions(post_id=post_id, user_id=user_id, reactionType=reaction_type)
        post_like.save()


def react_to_comment(user_id, comment_id, reaction_type):
    try:
        comment_like = CommentReactions.objects.get(comment_id=comment_id, user_id=user_id)
        if comment_like.reactionType == reaction_type:
            comment_like.delete()
        else:
            comment_like.reactionType = reaction_type
            comment_like.save()
    except ObjectDoesNotExist:
        comment_like = CommentReactions(comment_id=comment_id, user_id=user_id, reactionType=reaction_type)
        comment_like.save()


def get_user_posts(user_id):
    return list(Post.objects.filter(user__id=user_id).values_list('id', flat=True))


def get_posts_with_more_positive_reactions():
    return list(Post.objects.values('id').annotate(positiveCount=Count('postreactions__reactionType', filter=Q(postreactions__reactionType__in=['LIKE', 'LOVE', 'HAHA', 'WOW'])), negativeCount=Count('postreactions__reactionType', filter=Q(postreactions__reactionType__in=['SAD', 'ANGRY']))).filter(positiveCount__gt=F('negativeCount')).values_list('id', flat=True))


def get_posts_reacted_by_user(user_id):
    return list(PostReactions.objects.filter(user_id=user_id).values_list('post_id', flat=True))


def get_reactions_to_post(post_id):
    return list(PostReactions.objects.filter(post_id=post_id).annotate(name=F('user__userName'), profile_pic=F('user__userPhoto'), reaction=F('reactionType')).values('user_id', 'name', 'profile_pic', 'reaction'))


def get_reaction_metrics(post_id):
    postReactions = PostReactions.objects.filter(post_id=post_id).values('reactionType').annotate(reaction_count=Count('reactionType'))
    reactionData = {}
    for reaction in postReactions:
        reactionData[reaction['reactionType']] = reaction['reaction_count']
    return reactionData


def get_total_reaction_count():
    return PostReactions.objects.count()


def get_replies_for_comment(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if comment.commented_on is not None:
        raise SuspiciousOperation('Bad Request')
    else:
        replyToComment = Comment.objects.select_related('user').filter(commented_on=comment.commented_on)
        replyData = []
        for reply in replyToComment:
            replyData.append(getReplyData(reply))
        return replyData


def delete_post(post_id):
    post = Post.objects.get(pk=post_id)
    post.delete()
