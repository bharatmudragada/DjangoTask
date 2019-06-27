from .models import User, Post, PostLikes, Comment, CommentLikes
from django.core.exceptions import ObjectDoesNotExist
import datetime


reactions = {'Li': 'Like', 'Lo': 'Love', 'Ha': 'Haha', 'Wo': 'Wow', 'Sa': 'Sad', 'An': 'Angry'}


def getReactionKey(value):
    for k in reactions:
        if reactions[k] == value:
            return k
    return None


def getReactionTypes(reactionTypes):
    reactionsData = []
    for reaction in reactionTypes:
        reactionsData.append(reactions[reaction['reactionType']])
    return reactionsData


def getCommentData(com):
    commentData = {}
    commentData["comment_id"] = com.pk
    commenter = {"user_id": com.userId.pk, "name": com.userId.userName, "profile_pic_url": com.userId.userPhoto}
    commentData["commenter"] = commenter
    commentData["commented_at"] = str(com.commentedTime)
    commentData["comment_content"] = com.commentText
    likesOfComment = CommentLikes.objects.filter(commentId=com.pk)
    comment_likes_count = likesOfComment.count()
    comment_reactionTypes = likesOfComment.values('reactionType').distinct()
    comment_reactionsData = getReactionTypes(comment_reactionTypes)
    commentData["reactions"] = {"count": comment_likes_count, "type": comment_reactionsData}
    return commentData


def get_post_content(post):
    postData = {}
    commentOfPost = Comment.objects.filter(postId=post.pk, replyId=None)
    likesOfPost = PostLikes.objects.filter(postId=post.pk)
    count = likesOfPost.count()
    reactionTypes = likesOfPost.values('reactionType').distinct()
    reactionsData = getReactionTypes(reactionTypes)
    postData["post_id"] = post.pk
    postData["posted_by"] = {"name": post.userId.userName, "user_id": post.userId.pk,
                             "profile_pic_url": post.userId.userPhoto}
    postData["posted_at"] = str(post.postedTime)
    postData["post_content"] = post.postBody
    postData["reactions"] = {"count": count, "type": reactionsData}
    commentsArray = []
    for com in commentOfPost:
        commentData = getCommentData(com)
        replyOfComment = Comment.objects.filter(replyId=com.pk)
        replysArray = []
        for reply in replyOfComment:
            replyData = getCommentData(reply)
            replysArray.append(replyData)
        commentData["replies_count"] = len(replysArray)
        commentData["replies"] = replysArray
        commentsArray.append(commentData)
    postData["comments"] = commentsArray
    postData["comments_count"] = len(commentsArray)
    return postData


def get_post(post_id):
    post = Post.objects.get(pk=post_id)
    return get_post_content(post)


def create_post(user_id, post_content):
    user = User.objects.get(pk=user_id)
    print(user)
    post = Post(userId=user, postBody=post_content, postedTime=datetime.datetime.now())
    post.save()
    return post.pk


def add_comment(post_id, comment_user_id, comment_text):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=comment_user_id)
    comment = Comment(postId=post, replyId=None, userId=user, commentText=comment_text, commentedTime=datetime.datetime.now())
    comment.save()
    return comment.pk


def reply_to_comment(comment_id, reply_user_id, reply_text):
    comment = Comment.objects.get(pk=comment_id)
    user = User.objects.get(pk=reply_user_id)
    reply = Comment(postId=comment.postId, replyId=comment, userId=user, commentText=reply_text, commentedTime=datetime.datetime.now())
    reply.save()
    return reply.pk


def react_to_post(user_id, post_id, reaction_type):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=user_id)
    try:
        post_like = PostLikes.objects.get(postId=post, likeUserId=user)
        if reactions[post_like.reactionType] == reaction_type:
            post_like.delete()
        else:
            post_like.reactionType = getReactionKey(reaction_type)
            post_like.save()
    except ObjectDoesNotExist:
        post_like = PostLikes(postId=post, likeUserId=user, reactionType=getReactionKey(reaction_type))
        post_like.save()


def react_to_comment(user_id, comment_id, reaction_type):
    comment = Comment.objects.get(pk=comment_id)
    user = User.objects.get(pk=user_id)
    try:
        comment_like = CommentLikes.objects.get(commentId=comment, userId=user)
        if reactions[comment_like.reactionType] == reaction_type:
            comment_like.delete()
        else:
            comment_like.reactionType = getReactionKey(reaction_type)
            comment_like.save()
    except ObjectDoesNotExist:
        comment_like = CommentLikes(commentId=comment, userId=user, reactionType=getReactionKey(reaction_type))
        comment_like.save()


def get_user_posts(user_id):
    user = User.objects.get(pk=user_id)
    posts = Post.objects.filter(userId=user)
    userPosts = []
    for post in posts:
        userPosts.append(get_post(post.pk))
    return userPosts


def reactions_count(post):
    postReactions = PostLikes.objects.filter(postId=post)
    reactionCount = {'Love': 0, 'Like': 0, 'Haha': 0, 'Wow': 0, 'Sad': 0, 'Angry': 0}
    for reaction in postReactions:
        reactionCount[reactions[reaction.reactionType]] += 1
    return reactionCount


def get_posts_with_more_positive_reactions():
    allPosts = Post.objects.all()
    positivePosts = []
    for post in allPosts:
        count = reactions_count(post)
        positive = count['Love'] + count['Like'] + count['Wow'] + count['Haha']
        negative = count['Sad'] + count['Angry']
        if positive > negative:
            positivePosts.append(get_post_content(post))
    return positivePosts


def get_posts_reacted_by_user(user_id):
    userPosts = PostLikes.objects.filter(likeUserId=user_id)
    userReactedPosts = []
    for post in userPosts:
        userReactedPosts.append(get_post_content(post.postId))
    return userReactedPosts


def get_reactions_to_post(post_id):
    post = Post.objects.get(pk=post_id)
    postReactions = PostLikes.objects.filter(postId=post)
    postReactionData = []
    for reaction in postReactions:
        reactionData = {"user_id": reaction.likeUserId.pk, "name": reaction.likeUserId.userName, "profile_pic": reaction.likeUserId.userPhoto, "reaction": reactions[reaction.reactionType]}
        postReactionData.append(reactionData)
    return postReactionData


def get_reaction_metrics(post_id):
    post = Post.objects.get(pk=post_id)
    return reactions_count(post)


def get_total_reaction_count():
    return PostLikes.objects.count()