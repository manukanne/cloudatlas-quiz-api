from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, StringField, BooleanField, \
    SequenceField, ListField, ReferenceField, EmailField, DO_NOTHING as DELETION_RULE_DO_NOTHING


class User(Document):
    """
    MongoDB User document
    """
    email = EmailField(primary_key=True)
    first_name = StringField(required=True, min_length=3, max_length=30)
    last_name = StringField(required=True, min_length=3, max_length=30)
    password_hash = StringField(required=True)
    disabled = BooleanField(default=True)


class Category(Document):
    """
    MongoDB Category document
    """
    identifier = SequenceField(primary_key=True)
    title = StringField(unique=True, min_length=3, max_length=75)
    description = StringField(max_length=255)


class Answer(EmbeddedDocument):
    """
    MongoDB embedded Answer document
    """
    identifier = SequenceField(primary_key=True)
    answer_text = StringField(required=True, max_length=255)
    is_correct = BooleanField()


class Question(EmbeddedDocument):
    """
    MongoDB embedded Question document
    """
    identifier = SequenceField(primary_key=True)
    title = StringField(required=True, min_length=3, max_length=500)

    answers = ListField(EmbeddedDocumentField(Answer))


class Quiz(Document):
    """
    MongoDB Quiz document
    """
    identifier = SequenceField(primary_key=True)
    title = StringField(required=True, min_length=3, max_length=75)
    description = StringField(required=False, max_length=255)

    owner = ReferenceField(User)
    questions = ListField(EmbeddedDocumentField(Question))
    categories = ListField(ReferenceField(Category, reverse_delete_rule=DELETION_RULE_DO_NOTHING))
