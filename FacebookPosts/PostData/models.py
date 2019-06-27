from django.db import models

# Create your models here.

Reactions = (
    ('Li', 'Like'),
    ('Lo', 'Love'),
    ('Ha', 'Haha'),
    ('Wo', 'Wow'),
    ('Sa', 'Sad'),
    ('An', 'Angry')
)


class User(models.Model):
    userName = models.CharField(max_length=50)
    userPhoto = models.CharField(max_length=30)

    def __str__(self):
        return self.userName


class Post(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    postBody = models.CharField(max_length=200)
    postedTime = models.DateTimeField()

    def __str__(self):
        return str(self.pk) + ", " + str(self.userId) + ", " + self.postBody


class PostLikes(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    likeUserId = models.ForeignKey(User, on_delete=models.CASCADE)
    reactionType = models.CharField(max_length=2, choices=Reactions)

    def __str__(self):
        return str(self.postId.postBody) + ", " + str(self.likeUserId) + ", " + self.reactionType


class Comment(models.Model):
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    replyId = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, default=None)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    commentText = models.CharField(max_length=100)
    commentedTime = models.DateTimeField()

    def __str__(self):
        if not self.replyId == None:
            return str(self.pk) + ", " + str(self.replyId.pk) + ", " + str(self.userId) + ", " + self.commentText
        else:
            return str(self.pk) + ", " + str(self.userId) + ", " + self.commentText


class CommentLikes(models.Model):
    commentId = models.ForeignKey(Comment, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    reactionType = models.CharField(max_length=2, choices=Reactions)

    def __str__(self):
        return str(self.commentId.commentText) + ", " + str(self.userId) + ", " + self.reactionType

