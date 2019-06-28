from .models import Post, PostReactions, Comment, CommentReactions
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.db.models import Count, F, Q
from django.core.exceptions import SuspiciousOperation


def getUserData(user):
    return {"user_id": user.pk, "name": user.userName, "profile_pic_url": user.userPhoto}


def getReactions(reactions):
    reactionTypes = []
    for reaction in reactions:
        reactionTypes.append(reaction['reactionType'])
    return reactionTypes

def getCommentData(comment):

    reactionOfComment = CommentReactions.objects.filter(comment=comment.pk)
    comment_likes_count = reactionOfComment.count()
    comment_reactionTypes = reactionOfComment.values('reactionType').distinct()

    commentData = {}
    commentData["comment_id"] = comment.pk
    commenter = getUserData(comment.user)
    commentData["commenter"] = commenter
    commentData["commented_at"] = comment.commentedTime.strftime('%y-%m-%d %H:%M:%S.%f')
    commentData["comment_content"] = comment.commentText
    commentData["reactions"] = {"count": comment_likes_count, "type": getReactions(comment_reactionTypes)}

    return commentData


def reactions_count(post):
    postReactions = PostReactions.objects.filter(post=post).values('reactionType').annotate(reaction_count=Count('reactionType'))
    reactionData = {}
    for reaction in postReactions:
        reactionData[reaction['reactionType']] = reaction['reaction_count']
    return reactionData


def getReplyData(comment):
    commentData = {}
    commentData["comment_id"] = comment.pk
    commenter = getUserData(comment.user)
    commentData["commenter"] = commenter
    commentData["commented_at"] = comment.commentedTime.strftime('%y-%m-%d %H:%M:%S.%f')
    commentData["comment_content"] = comment.commentText
    return commentData


def get_post_content(post):

    postData = {}
    commentOfPost = Comment.objects.filter(post=post.pk, commented_on=None)
    postReactions = PostReactions.objects.filter(post=post.pk)
    count = postReactions.count()
    reactionTypes = getReactions(postReactions.values('reactionType').distinct())

    commentsArray = []
    for com in commentOfPost:
        commentData = getCommentData(com)
        replyOfComment = Comment.objects.filter(commented_on=com.pk)
        replysArray = []
        for reply in replyOfComment:
            replyData = getCommentData(reply)
            replysArray.append(replyData)
        commentData["replies_count"] = len(replysArray)
        commentData["replies"] = replysArray
        commentsArray.append(commentData)

    postData["post_id"] = post.pk
    postData["posted_by"] = getUserData(post.user)
    postData["posted_at"] = post.postedTime.strftime('%y-%m-%d %H:%M:%S.%f')
    postData["post_content"] = post.postBody
    postData["reactions"] = {"count": count, "type": reactionTypes}
    postData["comments"] = commentsArray
    postData["comments_count"] = len(commentsArray)
    return postData


def get_post(post_id):
    post = Post.objects.get(pk=post_id)
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
    comment = Comment.objects.get(pk=comment_id)
    comment_on_id = comment.commented_on.id
    if comment_on_id is not None:
        comment = Comment.objects.get(pk=comment_on_id)
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
    post = Post.objects.get(pk=post_id)
    return reactions_count(post)


def get_total_reaction_count():
    return PostReactions.objects.count()


def get_replies_for_comment(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if comment.commented_on is not None:
        raise SuspiciousOperation('Bad Request')
    else:
        replyToComment = Comment.objects.filter(commented_on_id=comment_id)
        replyData = []
        for reply in replyToComment:
            replyData.append(getReplyData(reply))
        return replyData


def delete_post(post_id):
    post = Post.objects.get(pk=post_id)
    post.delete()
