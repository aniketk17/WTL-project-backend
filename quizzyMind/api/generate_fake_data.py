import random
from faker import Faker
from api.models import Category, Quiz, Question, Option, QuizSubmission, QuizSubmissionAnswer
from authentication.models import User, Profile

fake = Faker()

def generate_fake_data():
    create_users(5)
    create_categories(3)
    create_quizzes(5)
    create_questions(20)
    create_options()
    create_submissions(10)

    print("Random data generated successfully!")

def create_users(count):
    """Create random users with profiles"""
    for _ in range(count):
        user = User.objects.create_user(
            email=fake.email(),
            username=fake.user_name(),
            password="password123"
        )
        
        # Check if a profile already exists
        if not hasattr(user, 'profile'):
            Profile.objects.create(
                user=user,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=fake.phone_number()[:10],
                profile_pic=fake.image_url(),
                bio=fake.sentence(),
                institute_name=fake.company(),
                address=fake.address()
            )

def create_categories(count):
    """Create random quiz categories"""
    for _ in range(count):
        Category.objects.create(name=fake.word())

def create_quizzes(count):
    """Create random quizzes linked to categories"""
    categories = list(Category.objects.all())
    for _ in range(count):
        Quiz.objects.create(
            title=fake.sentence(),
            description=fake.paragraph(),
            category=random.choice(categories)
        )

def create_questions(count):
    """Create random questions for quizzes"""
    quizzes = list(Quiz.objects.all())
    for _ in range(count):
        quiz = random.choice(quizzes)
        question_number = Question.objects.filter(quiz=quiz).count() + 1
        Question.objects.create(
            quiz=quiz,
            text=fake.sentence(),
            question_number=question_number
        )

def create_options():
    """Create 4 options per question, with one correct answer"""
    questions = list(Question.objects.all())
    for question in questions:
        options = []
        correct_answer = random.randint(0, 3)  # Randomly choose a correct option
        for i in range(4):
            options.append(Option(
                question=question,
                option_text=fake.sentence(),
                is_correct=(i == correct_answer)
            ))
        Option.objects.bulk_create(options)

def create_submissions(count):
    """Create random quiz submissions with answers"""
    users = list(User.objects.all())
    quizzes = list(Quiz.objects.all())

    for _ in range(count):
        user = random.choice(users)
        quiz = random.choice(quizzes)
        submission = QuizSubmission.objects.create(user=user, quiz=quiz, score=0)

        questions = quiz.questions.all()
        score = 0
        for question in questions:
            options = list(question.options.all())
            selected_option = random.choice(options)
            is_correct = selected_option.is_correct

            QuizSubmissionAnswer.objects.create(
                submission=submission,
                question=question,
                selected_option=selected_option.option_text,
                is_correct=is_correct
            )

            if is_correct:
                score += 1

        submission.score = score
        submission.save()

