import pytest
from PostData.Operations import *
from PostData.models import *


pytestmark = pytest.mark.django_db


class TestCreatePost:

    @pytest.fixture
    def setup_post_data(self):
        user = User.objects.create(username="bharat", userPhoto="https://bharat.png")
        return user.id

    def test_create_post(self, setup_post_data):

        user_id = setup_post_data

        count_before_insertion = Post.objects.count()
        post_id = create_post(user_id=user_id, post_content="This is the first post")
        post = Post.objects.get(pk=post_id)

        assert Post.objects.count() == count_before_insertion + 1
        assert post.user_id == user_id
        assert post.postBody == "This is the first post"


class TestAddComment:

    @pytest.fixture
    def setup_comment_data(self):
        user = User.objects.create(username='bharat')
        post = Post.objects.create(user=user, postBody="This is comment post")
        return user.id, post.id

    def test_add_comment(self, setup_comment_data):

        user_id, post_id = setup_comment_data

        count_before_insertion = Comment.objects.count()
        comment_id = add_comment(post_id=post_id, comment_user_id=user_id, comment_text="This is comment")
        comment = Comment.objects.get(pk=comment_id)

        assert Comment.objects.count() == count_before_insertion + 1
        assert comment.user_id == user_id
        assert comment.commentText == "This is comment"
        assert comment.post_id == post_id

    def test_add_comment_multiple_insertions(self, setup_comment_data):

        user_id, post_id = setup_comment_data

        count_before_insertion = Comment.objects.filter(post_id=post_id).count()
        comment = add_comment(post_id=post_id, comment_user_id=user_id, comment_text="This is comment")
        comment_two = add_comment(post_id=post_id, comment_user_id=user_id, comment_text="This is comment 2")
        comment_three = add_comment(post_id=post_id, comment_user_id=user_id, comment_text="This is comment 3")

        assert Comment.objects.filter(post_id=post_id).count() == count_before_insertion + 3
        assert Comment.objects.get(pk=comment).commentText == "This is comment"
        assert Comment.objects.get(pk=comment_two).commentText == "This is comment 2"
        assert Comment.objects.get(pk=comment_three).commentText == "This is comment 3"


class TestReplyToComment:

    @pytest.fixture
    def setup_reply_data(self):
        user = User.objects.create(username='bharat')
        post = Post.objects.create(user=user, postBody='This is reply post')
        comment = Comment.objects.create(post=post, commented_on=None, user=user, commentText="This is a comment")
        return user.id, post.id, comment.id

    def test_reply_comment(self, setup_reply_data):

        user_id, post_id, comment_id = setup_reply_data

        count_before_insertion = Comment.objects.count()
        reply_id = reply_to_comment(comment_id=comment_id, reply_user_id=user_id, reply_text="This is another reply")
        reply = Comment.objects.get(pk=reply_id)

        assert Comment.objects.count() == count_before_insertion + 1
        assert reply.user_id == user_id
        assert reply.commentText == "This is another reply"

    @pytest.fixture
    def setup_reply_to_reply(self, setup_reply_data):
        user_id, post_id, comment_id = setup_reply_data
        reply_id = reply_to_comment(comment_id=comment_id, reply_user_id=user_id, reply_text="This is another reply")
        return user_id, post_id, comment_id, reply_id

    def test_reply_comment_reply_to_reply(self, setup_reply_to_reply):

        user_id, post_id, comment_id, reply_id = setup_reply_to_reply

        reply_id = reply_to_comment(comment_id=comment_id, reply_user_id=user_id, reply_text="This is another reply")

        reply_to_reply_id = reply_to_comment(comment_id=reply_id, reply_user_id=user_id, reply_text="This is reply to reply")
        reply_to_reply = Comment.objects.get(pk=reply_to_reply_id)

        assert reply_to_reply.commented_on_id == comment_id
        assert reply_to_reply.user_id == user_id
        assert reply_to_reply.commentText == "This is reply to reply"


class TestReactToPost:

    @pytest.fixture
    def setup_react_to_post(self):
        user = User.objects.create(username='bharat')
        post = Post.objects.create(user=user, postBody='This is reply post')
        return user.id, post.id

    def test_react_to_post(self, setup_react_to_post):

        user_id, post_id = setup_react_to_post

        count_before_insertion = PostReactions.objects.count()
        react_to_post(user_id=user_id, post_id=post_id, reaction_type="LOVE")
        reaction = PostReactions.objects.get(user_id=user_id, post_id=post_id)

        assert PostReactions.objects.count() == count_before_insertion + 1
        assert reaction.reactionType == "LOVE"

    @pytest.fixture
    def setup_react_to_post_different_reaction(self, setup_react_to_post):
        user_id, post_id = setup_react_to_post
        PostReactions.objects.create(user_id=user_id, post_id=post_id, reactionType="LOVE")
        return user_id, post_id

    def test_react_to_post_different_reaction(self, setup_react_to_post_different_reaction):

        user_id, post_id = setup_react_to_post_different_reaction

        count_before_insertion = PostReactions.objects.count()
        react_to_post(user_id=user_id, post_id=post_id, reaction_type="LIKE")
        reaction = PostReactions.objects.get(user_id=user_id, post_id=post_id)

        assert PostReactions.objects.count() == count_before_insertion
        assert reaction.reactionType == "LIKE"

    @pytest.fixture
    def setup_react_to_post_same_reaction(self, setup_react_to_post):
        user_id, post_id = setup_react_to_post
        PostReactions.objects.create(user_id=user_id, post_id=post_id, reactionType="LIKE")
        return user_id, post_id

    def test_react_to_post_same_reaction(self, setup_react_to_post_same_reaction):

        user_id, post_id = setup_react_to_post_same_reaction

        count_before_insertion = PostReactions.objects.count()
        react_to_post(user_id=user_id, post_id=post_id, reaction_type="LIKE")

        assert PostReactions.objects.count() == count_before_insertion - 1

        with pytest.raises(ObjectDoesNotExist) as e:
            PostReactions.objects.get(user_id=user_id, post_id=post_id)


class TestReactToComment:

    @pytest.fixture
    def setup_react_to_comment(self):
        user = User.objects.create(username='bharat')
        post = Post.objects.create(user=user, postBody='This is reply post')
        comment = Comment.objects.create(user=user, post=post, commented_on=None, commentText="This is a comment")
        return user.id, comment.id

    def test_react_to_comment(self, setup_react_to_comment):

        user_id, comment_id = setup_react_to_comment

        count_before_insertion = CommentReactions.objects.count()
        react_to_comment(user_id=user_id, comment_id=comment_id, reaction_type="LOVE")
        reaction = CommentReactions.objects.get(user_id=user_id, comment_id=comment_id)

        assert CommentReactions.objects.count() == count_before_insertion + 1
        assert reaction.reactionType == "LOVE"

    @pytest.fixture
    def setup_react_to_comment_different_insertion(self, setup_react_to_comment):
        user_id, comment_id = setup_react_to_comment
        CommentReactions.objects.create(user_id=user_id, comment_id=comment_id, reactionType="LOVE")
        return user_id, comment_id

    def test_react_to_comment_different_insertion(self, setup_react_to_comment_different_insertion):

        user_id, comment_id = setup_react_to_comment_different_insertion

        count_before_insertion = CommentReactions.objects.count()
        react_to_comment(user_id=user_id, comment_id=comment_id, reaction_type="LIKE")
        reaction = CommentReactions.objects.get(user_id=user_id, comment_id=comment_id)

        assert CommentReactions.objects.count() == count_before_insertion
        assert reaction.reactionType == "LIKE"

    @pytest.fixture
    def setup_react_to_comment_same_insertion(self, setup_react_to_comment):
        user_id, comment_id = setup_react_to_comment
        CommentReactions.objects.create(user_id=user_id, comment_id=comment_id, reactionType="LIKE")
        return user_id, comment_id

    def test_react_to_comment_same_insertion(self, setup_react_to_comment_same_insertion):

        user_id, comment_id = setup_react_to_comment_same_insertion

        count_before_insertion = CommentReactions.objects.count()
        react_to_comment(user_id=user_id, comment_id=comment_id, reaction_type="LIKE")

        assert CommentReactions.objects.count() == count_before_insertion - 1

        with pytest.raises(ObjectDoesNotExist) as e:
            CommentReactions.objects.get(user_id=user_id, comment_id=comment_id)


class TestGetUserPosts:

    @pytest.fixture
    def setup_get_user_posts(self):
        user = User.objects.create(username='bharat')
        post_one = Post.objects.create(user=user, postBody='This is first post')
        post_two = Post.objects.create(user=user, postBody='This is second post')
        post_three = Post.objects.create(user=user, postBody='This is third post')
        post_four = Post.objects.create(user=user, postBody='This is fourth post')
        return user.id, [post_one.id, post_two.id, post_three.id, post_four.id]

    def test_get_user_posts(self, setup_get_user_posts):

        user_id, post_ids = setup_get_user_posts

        posts = get_user_posts(user_id)

        assert posts == post_ids

    @pytest.fixture
    def setup_get_user_posts_other_user_posts(self):
        user = User.objects.create(username='bharat')
        user_two = User.objects.create(username='bharat mudragada')
        post = Post.objects.create(user=user_two, postBody='This is first post')
        return user.id, post.id

    def test_get_user_posts_other_user_posts(self, setup_get_user_posts_other_user_posts):

        user_id, post_id = setup_get_user_posts_other_user_posts

        posts = get_user_posts(user_id)

        assert post_id not in posts


class TestGetPostsWithMorePositiveCount:

    @pytest.fixture
    def setup_user_post(self):
        user = User.objects.create(username='bharat')
        user_two = User.objects.create(username='bharat mudragada')
        user_three = User.objects.create(username='bharat mudragada 2')
        post = Post.objects.create(user=user, postBody='This is first post')
        return user.id, user_two.id, user_three.id, post.id

    @pytest.fixture
    def setup_posts_with_more_positive_reactions(self, setup_user_post):
        user_id, user_two_id, user_three_id, post_id = setup_user_post
        PostReactions.objects.create(user_id=user_id, post_id=post_id, reactionType="LOVE")
        PostReactions.objects.create(user_id=user_two_id, post_id=post_id, reactionType="LIKE")
        PostReactions.objects.create(user_id=user_three_id, post_id=post_id, reactionType="LIKE")
        return post_id

    def test_get_posts_with_positive_reactions(self, setup_posts_with_more_positive_reactions):

        post_id = setup_posts_with_more_positive_reactions
        posts = get_posts_with_more_positive_reactions()

        assert post_id in posts

    @pytest.fixture
    def setup_posts_with_more_negative_reactions(self, setup_user_post):
        user_id, user_two_id, user_three_id, post_id = setup_user_post
        PostReactions.objects.create(user_id=user_id, post_id=post_id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_two_id, post_id=post_id, reactionType="LIKE")
        PostReactions.objects.create(user_id=user_three_id, post_id=post_id, reactionType="ANGRY")
        return post_id

    def test_get_posts_with_negative_reaction(self, setup_posts_with_more_negative_reactions):
        post_id = setup_posts_with_more_negative_reactions
        posts = get_posts_with_more_positive_reactions()

        assert post_id not in posts

    @pytest.fixture
    def setup_posts_with_equal_reactions(self, setup_user_post):
        user_id, user_two_id, user_three_id, post_id = setup_user_post
        PostReactions.objects.create(user_id=user_id, post_id=post_id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_two_id, post_id=post_id, reactionType="LIKE")
        return post_id

    def test_get_posts_with_equal_reaction(self, setup_posts_with_equal_reactions):
        post_id = setup_posts_with_equal_reactions
        posts = get_posts_with_more_positive_reactions()

        assert post_id not in posts


class TestPostsReactedByUser:

    @pytest.fixture
    def setup_user_post(self):
        user = User.objects.create(username='bharat')
        user_two = User.objects.create(username='bharat mudragada')
        post = Post.objects.create(user=user, postBody='This is first post')
        return user.id, user_two.id, post.id

    def test_posts_reacted_by_user(self, setup_user_post):

        user_id, user_two_id, post_id = setup_user_post
        PostReactions.objects.create(user_id=user_id, post_id=post_id, reactionType="SAD")

        posts = get_posts_reacted_by_user(user_id)

        assert post_id in posts

    def test_posts_not_reacted_by_user(self, setup_user_post):

        user_id, user_two_id, post_id = setup_user_post
        PostReactions.objects.create(user_id=user_two_id, post_id=post_id, reactionType="SAD")

        posts = get_posts_reacted_by_user(user_id)

        assert post_id not in posts


class TestReactionToPost:

    @pytest.fixture
    def setup_reactions_to_post(self):
        user = User.objects.create(username='bharat', userPhoto="https://bharat.png")
        user_two = User.objects.create(username='bharat mudragada', userPhoto="https://bharatmudragada.png")
        post = Post.objects.create(user=user, postBody='This is first post')
        post_two = Post.objects.create(user=user, postBody='This is second post')
        return user, user_two, post, post_two

    def test_reactions_to_post(self, setup_reactions_to_post):

        user, user_two, post, post_two = setup_reactions_to_post
        PostReactions.objects.create(user_id=user.id, post_id=post.id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_two.id, post_id=post.id, reactionType="SAD")

        reactions = get_reactions_to_post(post.id)

        assert reactions[0]['user_id'] == user.id
        assert reactions[1]['user_id'] == user_two.id
        assert reactions[0]['name'] == user.username
        assert reactions[1]['name'] == user_two.username
        assert reactions[0]['profile_pic'] == user.userPhoto
        assert reactions[1]['profile_pic'] == user_two.userPhoto
        assert reactions[0]['reaction'] == PostReactions.objects.get(user_id=user.id, post_id=post.id).reactionType
        assert reactions[1]['reaction'] == PostReactions.objects.get(user_id=user_two.id, post_id=post.id).reactionType

    def test_reactions_to_different_post(self, setup_reactions_to_post):
        user, user_two, post, post_two = setup_reactions_to_post
        PostReactions.objects.create(user_id=user.id, post_id=post_two.id, reactionType="SAD")

        reactions = get_reactions_to_post(post.id)

        reaction_users = [reaction['user_id'] for reaction in reactions]

        assert user.id not in reaction_users


class TestReactionMetrics:

    @pytest.fixture
    def setup_user_post(self):
        user = User.objects.create(username='bharat')
        user_two = User.objects.create(username='bharat 2')
        user_three = User.objects.create(username='bharat 3')
        user_four = User.objects.create(username='bharat 4')
        post = Post.objects.create(user=user, postBody='This is reply post')
        post_two = Post.objects.create(user=user, postBody='This is post')
        return user, user_two, user_three, user_four, post, post_two

    def test_post_reaction_metrics(self, setup_user_post):

        user, user_two, user_three, user_four, post, post_two = setup_user_post

        PostReactions.objects.create(user_id=user.id, post_id=post.id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_two.id, post_id=post.id, reactionType="LOVE")
        PostReactions.objects.create(user_id=user_three.id, post_id=post.id, reactionType="LIKE")
        PostReactions.objects.create(user_id=user_four.id, post_id=post.id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_four.id, post_id=post_two.id, reactionType="SAD")

        metrics = get_reaction_metrics(post.id)

        assert metrics["SAD"] == 2
        assert metrics["LOVE"] == 1
        assert metrics["LIKE"] == 1

    def test_post_reaction_mertics_with_no_reactions(self, setup_user_post):

        user, user_two, user_three, user_four, post, post_two = setup_user_post

        metrics = get_reaction_metrics(post.id)

        assert metrics == {}


class TestTotalReactionCount:

    @pytest.fixture
    def setup_user_post(self):
        user = User.objects.create(username='bharat')
        user_two = User.objects.create(username='bharat 2')
        user_three = User.objects.create(username='bharat 3')
        user_four = User.objects.create(username='bharat 4')
        post = Post.objects.create(user=user, postBody='This is reply post')
        post_two = Post.objects.create(user=user, postBody='This is post')
        return user, user_two, user_three, user_four, post, post_two

    def test_total_reaction_count(self, setup_user_post):

        user, user_two, user_three, user_four, post, post_two = setup_user_post

        reaction_count_before_insertion = PostReactions.objects.count()

        PostReactions.objects.create(user_id=user.id, post_id=post.id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_two.id, post_id=post.id, reactionType="LOVE")
        PostReactions.objects.create(user_id=user_three.id, post_id=post.id, reactionType="LIKE")
        PostReactions.objects.create(user_id=user_four.id, post_id=post.id, reactionType="SAD")
        PostReactions.objects.create(user_id=user_four.id, post_id=post_two.id, reactionType="SAD")

        count = get_total_reaction_count()

        assert count == reaction_count_before_insertion + 5


class TestRepliesToComment:

    @pytest.fixture
    def setup_user_post_comment(self):
        user = User.objects.create(username='bharat')
        post = Post.objects.create(user=user, postBody='This is reply post')
        comment = Comment.objects.create(user=user, post=post, commented_on=None, commentText="This is a comment")
        return user, comment

    def test_replies_to_comment(self, setup_user_post_comment):

        user, comment = setup_user_post_comment

        reply_one = Comment.objects.create(user_id=user.id, post_id=comment.post_id, commented_on=comment, commentText="This is reply 1")
        reply_two = Comment.objects.create(user_id=user.id, post_id=comment.post_id, commented_on=comment, commentText="This is reply 2")
        reply_three = Comment.objects.create(user_id=user.id, post_id=comment.post_id, commented_on=comment, commentText="This is reply 3")
        reply_four = Comment.objects.create(user_id=user.id, post_id=comment.post_id, commented_on=comment, commentText="This is reply 4")

        replies = get_replies_for_comment(comment.id)

        reply_ids = [reply['comment_id'] for reply in replies]

        assert [reply_one.id, reply_two.id, reply_three.id, reply_four.id] == reply_ids

        reply_one_data = None
        for reply in replies:
            if reply['comment_id'] == reply_one.id:
                reply_one_data = reply
                break

        assert reply_one_data['commenter']['user_id'] == user.id
        assert reply_one_data['commenter']['name'] == user.username
        assert reply_one_data['commenter']['profile_pic_url'] == user.userPhoto
        assert reply_one_data['comment_content'] == "This is reply 1"

    def test_not_a_comment(self, setup_user_post_comment):

        user, comment = setup_user_post_comment

        reply = Comment.objects.create(user_id=user.id, post_id=comment.post_id, commented_on=comment, commentText="This is reply 1")

        with pytest.raises(SuspiciousOperation) as e:
            get_replies_for_comment(reply.id)


class TestDeletePost:
    @pytest.fixture
    def setup_user_post(self):
        user = User.objects.create(username='bharat')
        post = Post.objects.create(user=user, postBody='This is first post')
        return user.id, post.id

    def test_delete_post(self, setup_user_post):

        user_id, post_id = setup_user_post

        delete_post(post_id)

        with pytest.raises(ObjectDoesNotExist) as e:
            delete_post(post_id)


class TestGetPost:

    @classmethod
    def setup_user_post(cls):
        user = User.objects.create(username='bharat', userPhoto="https://bharat.png")
        user_two = User.objects.create(username='karthik', userPhoto="https://karthik.png")
        user_three = User.objects.create(username='vamsi', userPhoto='https://vamsi.png')
        user_four = User.objects.create(username='krishna', userPhoto='https://krishna.png')
        post = Post.objects.create(user=user, postBody='This is first Post')
        return user, user_two, user_three, user_four, post

    @pytest.fixture
    def setup_get_post_data(self, setup_user_post):
        user, user_two, user_three, user_four, post = setup_user_post()

    def test_get_post_post_details(self, setup_get_post_data):
        user, user_two, user_three, user_four, post = setup_get_post_data
        post_data = get_post(post.id)

        assert post_data["post_id"] == post.id
        assert post_data["posted_by"] == {"name": post.user.username, "user_id": post.user.id, "profile_pic_url": post.user.userPhoto}
        assert post_data["post_content"] == post.postBody
        assert post_data["posted_at"] == post.postedTime.strftime('%y-%m-%d %H:%M:%S.%f')

    @pytest.fixture
    def setup_get_post_comment_data(self, setup_get_post_data):

        user, user_two, user_three, user_four, post = setup_get_post_data
        comment = Comment.objects.create(post=post, commented_on=None, user=user_two, commentText="This is a comment")
        return post, user_two, comment

    def test_get_post_comment_details(self, setup_get_post_comment_data):
        post, user, comment = setup_get_post_comment_data

        post_data = get_post(post.id)

        comment_ids = [comment["comment_id"] for comment in post_data["comments"]]
        
        assert comment.id in comment_ids

        comment_data = None
        for comment_details in post_data["comments"]:
            if comment_details["comment_id"] == comment.id:
                comment_data = comment_details
        
        assert comment_data["commenter"] == {"name": comment.user.username, "user_id": comment.user.id, "profile_pic_url": comment.user.userPhoto}
        assert comment_data["comment_content"] == comment.commentText
        assert comment_data["commented_at"] == comment.commentedTime.strftime('%y-%m-%d %H:%M:%S.%f')


    @pytest.fixture
    def setup_reaction_data(self, setup_get_post_data):

        user, user_two, user_three, user_four, post = setup_get_post_data
        PostReactions.objects.create(post=post, user=user, reactionType="LOVE")
        PostReactions.objects.create(post=post, user=user_two, reactionType="LIKE")
        PostReactions.objects.create(post=post, user=user_three, reactionType="WOW")
        PostReactions.objects.create(post=post, user=user_four, reactionType="WOW")
        return post

    def test_get_post_reaction_data(self, setup_reaction_data):

        post = setup_reaction_data

        post_data = get_post(post.id)

        assert post_data["reactions"]["count"] == 4
        assert post_data["reactions"]["type"].sort() == ["LOVE", "LIKE", "WOW"].sort()
        
    @pytest.fixture
    def setup_comment_reply(self, setup_get_post_data):
        
        user, user_two, user_three, user_four, post = setup_get_post_data
        comment = Comment.objects.create(post=post, commented_on=None, user=user_two, commentText="This is a comment")
        reply = Comment.objects.create(post=post, commented_on=comment, user=user_two, commentText="This is a reply")
        return user_two, reply, post, comment

    def test_get_post_reply_data(self, setup_comment_reply):

        user, reply, post, comment = setup_comment_reply

        post_data = get_post(post.id)
        comment_data = None
        for comment_details in post_data["comments"]:
            if comment_details["comment_id"] == comment.id:
                comment_data = comment_details
                break
        
        reply_ids = [reply["comment_id"] for reply in comment_data["replies"]]
        
        assert reply.id in reply_ids
        
        reply_data = None
        for reply_details in comment_data["replies"]:
            if reply_details["comment_id"] == reply.id:
                reply_data = reply_details
                break
        
        assert reply_data["commenter"] == {"name": reply.user.username, "user_id": reply.user.id, "profile_pic_url": reply.user.userPhoto}
        assert reply_data["comment_content"] == reply.commentText

    @pytest.fixture
    def setup_comment_reaction_data(self, setup_get_post_data):

        user, user_two, user_three, user_four, post = setup_get_post_data
        comment = Comment.objects.create(post=post, commented_on=None, user=user_two, commentText="This is a comment")
        CommentReactions.objects.create(comment=comment, user=user, reactionType="LOVE")
        CommentReactions.objects.create(comment=comment, user=user_two, reactionType="SAD")
        CommentReactions.objects.create(comment=comment, user=user_three, reactionType="LOVE")
        return post, comment

    def test_get_post_comment_reaction_details(self, setup_comment_reaction_data):
        post, comment = setup_comment_reaction_data

        post_data = get_post(post.id)

        comment_ids = [comment["comment_id"] for comment in post_data["comments"]]

        assert comment.id in comment_ids

        comment_data = None
        for comment_details in post_data["comments"]:
            if comment_details["comment_id"] == comment.id:
                comment_data = comment_details

        assert comment_data["reactions"]["count"] == 3
        assert comment_data["reactions"]["type"].sort() == ["LOVE", "SAD"].sort()

    @pytest.fixture
    def setup_comment_data(self, setup_get_post_data):
        user, user_two, user_three, user_four, post = setup_get_post_data
        comment = Comment.objects.create(post=post, commented_on=None, user=user, commentText="This is a comment")
        Comment.objects.create(post=post, commented_on=None, user=user_three, commentText="This is a comment 2")
        Comment.objects.create(post=post, commented_on=None, user=user_two, commentText="This is a comment 3")
        Comment.objects.create(post=post, commented_on=None, user=user_four, commentText="This is a comment 4")
        Comment.objects.create(post=post, commented_on=comment, user=user_two, commentText="This is a comment reply")
        return post

    def test_comment_count(self, setup_comment_data):
        post = setup_comment_data

        post_data = get_post(post.id)

        assert post_data["comments_count"] == Comment.objects.filter(post=post, commented_on=None).count()