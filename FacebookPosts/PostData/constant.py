import enum


class Reaction(enum.Enum):
    love = "LOVE"
    like = "LIKE"
    haha = "HAHA"
    wow = "WOW"
    sad = "SAD"
    angry = "Angry"

    @classmethod
    def get_reactions(cls):
        ReactionChoices = []
        for reaction in (Reaction):
            ReactionChoices.append((reaction.value, reaction.value))
        return tuple(ReactionChoices)