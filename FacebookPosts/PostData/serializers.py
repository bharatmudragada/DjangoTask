from rest_framework import serializers
from .models import *

date_format = '%y-%m-%d %H:%M:%S.%f'


class UserSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'userPhoto', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            userPhoto=validated_data["userPhoto"]
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'postBody',)
        extra_kwargs = {'postBody': {'write_only': True}}


class ReactionSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    type = serializers.ListField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserDataSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    name = serializers.CharField()
    profile_pic_url = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ReplySerializer(serializers.Serializer):

    comment_id = serializers.IntegerField()
    commented_at = serializers.DateTimeField(format=date_format)
    comment_content = serializers.CharField()

    commenter = UserDataSerializer()
    reactions = ReactionSerializer()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class CommentSerializer(ReplySerializer):

    replies_count = serializers.IntegerField()
    replies = ReplySerializer(many=True)


class GetPostSerializer(serializers.ModelSerializer):

    user = UserSerilaizer()
    reactions = ReactionSerializer()
    comments = CommentSerializer(many=True)
    comments_count = serializers.IntegerField()
    postedTime = serializers.DateTimeField(format=date_format)

    class Meta:
        model = Post
        fields = ('id', 'user', 'postBody', 'postedTime', 'comments', 'reactions', 'comments_count')


class AddCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'post', 'commentText')


class AddReplySerializer(serializers.ModelSerializer):

    commented_on = serializers.IntegerField(required=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'commented_on', 'commentText')


class PostReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostReactions
        fields = ('id', 'post', 'reactionType')


class CommentReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentReactions
        fields = ('id', 'comment', 'reactionType')


class IdSerializer(serializers.Serializer):

    id = serializers.IntegerField()


class CountSerializer(serializers.Serializer):

    total_count = serializers.IntegerField()


class PostIdSerializer(serializers.Serializer):

    post_ids = serializers.ListField(allow_empty=True, child=serializers.IntegerField())


class PostReactionSerializer(UserDataSerializer):

    reaction = serializers.CharField()


class ReactionMetricSerializer(serializers.Serializer):

    reactionType = serializers.CharField()
    reaction_count = serializers.IntegerField()


class CommentReplySerializer(serializers.ModelSerializer):

    user = UserSerilaizer()
    commentedTime = serializers.DateTimeField(format=date_format)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'commentedTime', 'commentText')
