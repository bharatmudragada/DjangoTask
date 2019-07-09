from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from PostData.serializers import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Q, Subquery
from .permisssions import *
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.decorators import protected_resource


def get_reaction_object(reaction_dic):
    return {"count": reaction_dic["count"], "type": list(reaction_dic["type"])}


def getCommentData(comment, commentReactions):
    comment_data = {}
    comment_data["comment_id"] = comment['id']
    comment_data["commenter"] = {"user_id": comment["user"], "name": comment["user__username"], "profile_pic_url": comment["user__userPhoto"]}
    comment_data["commented_at"] = comment['commentedTime']
    comment_data["comment_content"] = comment['commentText']
    comment_data["reactions"] = get_reaction_object(commentReactions)
    return comment_data


@api_view(['GET'])
@protected_resource(scopes=['read'])
def get_post(request, post_id):

    try:
        post = Post.objects.select_related('user').get(pk=post_id)
    except ObjectDoesNotExist:
        return Response("Post Does Not Exist", status.HTTP_400_BAD_REQUEST)

    comments = Comment.objects.select_related('user').filter(post=post, commented_on=None).values('id', 'commented_on', 'user', 'user__username', 'user__userPhoto', 'commentText', 'commentedTime')

    post_reactions = PostReactions.objects.filter(post=post).values_list('reactionType', flat=True)
    post.reactions = {"count": post_reactions.count(), "type": list(post_reactions.distinct())}

    comment_ids = comments.values('id')
    all_comment_replys = Comment.objects.select_related('user').filter(commented_on__in=Subquery(comment_ids)).values('id', 'commented_on', 'user', 'user__username', 'user__userPhoto', 'commentText', 'commentedTime')

    all_comment_ids = Comment.objects.filter(post=post).values('id')

    all_reply_reactions = CommentReactions.objects.filter(comment_id__in=Subquery(all_comment_ids)).values('comment_id', 'reactionType')

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
    for comment in comments:
        if comment['id'] in comment_reactions:
            comment_data = getCommentData(comment, comment_reactions[comment['id']])
        else:
            comment_data = getCommentData(comment, {"count": 0, "type": {}})
        replyArray = []
        if comment['id'] in comment_replys:
            for reply in comment_replys[comment['id']]:
                try:
                    replyReactions = comment_reactions[reply['id']]
                except KeyError:
                    replyReactions = {"count": 0, "type": []}
                replyArray.append(getCommentData(reply, replyReactions))
        comment_data["replies_count"] = len(replyArray)
        comment_data["replies"] = replyArray
        commentsArray.append(comment_data)

    post.comments = commentsArray

    post.comments_count = len(commentsArray)

    serializer = GetPostSerializer(post)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@protected_resource(scopes=['read'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerilaizer(users, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = UserSerilaizer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, ))
def create_post(request):
    serializer = PostCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, ))
def add_comment(request):
    serializer = AddCommentSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, ))
def reply_to_comment(request):
    serializer = AddReplySerializer(data=request.data)
    if serializer.is_valid():
        comment = Comment.objects.get(pk=request.data['commented_on'])
        if comment.commented_on is not None:
            comment = Comment.objects.get(id=comment.commented_on.id)

        serializer.save(user=request.user, commented_on=comment, post_id = comment.post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, ))
def react_to_post(request):
    serializer = PostReactionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            post_like = PostReactions.objects.get(post_id=request.data['post'], user=request.user)
            if post_like.reactionType == request.data['reactionType']:
                post_like.delete()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                post_like.reactionType = request.data['reactionType']
                post_like.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            post_like = PostReactions(post_id=request.data['post'], user=request.user, reactionType=request.data['reactionType'])
            post_like.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, ))
def react_to_comment(request):
    serializer = CommentReactionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            comment_like = CommentReactions.objects.get(comment_id=request.data['comment'], user=request.user)
            if comment_like.reactionType == request.data['reactionType']:
                comment_like.delete()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                comment_like.reactionType = request.data['reactionType']
                comment_like.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            comment_like = CommentReactions(comment_id=request.data['comment'], user=request.user, reactionType=request.data['reactionType'])
            comment_like.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@protected_resource(scopes=['read'])
def get_user_posts(request):
    posts = list(Post.objects.filter(user=request.user).values_list('id', flat=True))
    data = {"post_ids": posts}
    serializer = PostIdSerializer(data=data)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@protected_resource(scopes=['read'])
def get_posts_with_more_positive_reactions(request):
    posts = list(Post.objects.values('id').annotate(positiveCount=Count('postreactions__reactionType', filter=Q(postreactions__reactionType__in=['LIKE', 'LOVE', 'HAHA', 'WOW'])), negativeCount=Count('postreactions__reactionType', filter=Q(postreactions__reactionType__in=['SAD', 'ANGRY']))).filter(positiveCount__gt=F('negativeCount')).values_list('id', flat=True))
    data = {"post_ids": posts}
    serializer = PostIdSerializer(data=data)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@protected_resource(scopes=['read'])
def get_posts_reacted_by_user(request):
    posts = list(PostReactions.objects.filter(user=request.user).values_list('post_id', flat=True))
    data = {"post_ids": posts}
    serializer = PostIdSerializer(data=data)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@protected_resource(scopes=['read'])
def get_reactions_to_post(request):
    serializer = IdSerializer(data=request.data)
    if serializer.is_valid():
        reactions = list(PostReactions.objects.filter(post_id=request.data['id']).annotate(name=F('user__username'), profile_pic_url=F('user__userPhoto'), reaction=F('reactionType')).values('user_id', 'name', 'profile_pic_url', 'reaction'))
        data_serializer = PostReactionSerializer(data=reactions, many=True)
        if data_serializer.is_valid():
            return Response(data_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@protected_resource(scopes=['read'])
def get_reaction_metrics(request):

    serializer = IdSerializer(data=request.data)
    if serializer.is_valid():
        postReactions = list(PostReactions.objects.filter(post_id=request.data['id']).values('reactionType').annotate(reaction_count=Count('reactionType')))
        reaction_serializer = ReactionMetricSerializer(data=postReactions, many=True)
        if reaction_serializer.is_valid():
            return Response(reaction_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(reaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@protected_resource(scopes=['read'])
def get_total_reaction_count(request):
    count = PostReactions.objects.count()
    data = {"total_count": count}
    serializer = CountSerializer(data=data)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@protected_resource(scopes=['read'])
def get_replies_for_comment(request):
    serializer = IdSerializer(data=request.data)
    if serializer.is_valid():
        comment = Comment.objects.get(pk=request.data['id'])
        if comment.commented_on is not None:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            comment_replies = list(Comment.objects.select_related('user').filter(commented_on=request.data['id']))
            data_serializer = CommentReplySerializer(comment_replies, many=True)
            return Response(data_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((TokenHasReadWriteScope, IsOwner))
def delete_post(request):
    serializer = IdSerializer(data=request.data)
    if serializer.is_valid():
        post = Post.objects.get(pk=request.data['id'])
        post.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
