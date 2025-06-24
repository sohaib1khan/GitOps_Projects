from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
import random
import json
import os
import markdown
import datetime
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'  # Change this in production!

# Configure for reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Create templates and static directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# ======================= SIMPLE DATA HELPER =======================

class SimpleDataHelper:
    """One class to handle all JSON file operations"""

    @staticmethod
    def load_json(filename, default=None):
        """Load any JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default if default is not None else {}

    @staticmethod
    def save_json(filename, data):
        """Save any JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

# ======================= JSON FILE OPERATIONS =======================

def load_questions():
    return SimpleDataHelper.load_json('questions.json', [])

def save_questions(questions):
    SimpleDataHelper.save_json('questions.json', questions)

def load_progress():
    return SimpleDataHelper.load_json('progress.json', {})

def save_progress(progress):
    SimpleDataHelper.save_json('progress.json', progress)

def load_users():
    return SimpleDataHelper.load_json('users.json', {})

def load_flashcards():
    return SimpleDataHelper.load_json('flashcards.json', [])

def save_flashcards(flashcards):
    SimpleDataHelper.save_json('flashcards.json', flashcards)

def load_flashcard_progress(username=None):
    data = SimpleDataHelper.load_json('flashcard_progress.json', {})
    return data.get(username, {}) if username else data

def save_flashcard_progress_data(username, progress_data):
    data = SimpleDataHelper.load_json('flashcard_progress.json', {})
    data[username] = progress_data
    SimpleDataHelper.save_json('flashcard_progress.json', data)

# ======================= HELPER FUNCTIONS =======================

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def convert_markdown(text):
    """Convert markdown text to HTML"""
    return markdown.markdown(text)

def get_user_progress(username):
    """Get progress for a specific user"""
    progress = load_progress()
    return progress.get(username, {})

def save_user_progress(username, question_id, is_correct, score=None):
    """Save progress for a specific user and question with score support"""
    progress = load_progress()

    if username not in progress:
        progress[username] = {}

    progress[username][str(question_id)] = {
        'completed': True,
        'correct': is_correct,
        'score': score if score is not None else (1.0 if is_correct else 0.0),
        'timestamp': datetime.now().isoformat()
    }

    save_progress(progress)

def process_question_answers(form_data):
    """Process answers from form data, handling both single and multiple correct answers"""
    question_type = form_data.get('question_type', 'single')

    if question_type == 'multiple':
        # For multiple choice, get all checked correct answers
        correct_answers = []
        for i in range(1, 7):
            if form_data.get(f'correct_answer_{i}'):
                option_text = form_data.get(f'option{i}')
                if option_text and option_text.strip():
                    correct_answers.append(option_text.strip())
        return correct_answers if correct_answers else []
    else:
        # For single choice, return single answer as array for consistency
        correct_answer = form_data.get('correct_answer')
        return [correct_answer] if correct_answer else []

def check_user_answer(user_answers, correct_answers, question_type):
    """Check user answer(s) against correct answer(s) and return score"""
    if question_type == 'single':
        # Single answer - simple comparison
        user_answer = user_answers[0] if user_answers else ""
        correct_answer = correct_answers[0] if correct_answers else ""
        return {
            'is_correct': user_answer == correct_answer,
            'score': 1.0 if user_answer == correct_answer else 0.0,
            'partial_credit': False
        }
    else:
        # Multiple answers - calculate partial credit
        user_set = set(user_answers)
        correct_set = set(correct_answers)

        if not correct_set:  # No correct answers defined
            return {'is_correct': False, 'score': 0.0, 'partial_credit': False}

        # Calculate score
        correct_selected = len(user_set.intersection(correct_set))
        incorrect_selected = len(user_set - correct_set)
        total_correct = len(correct_set)

        # Scoring: +1 for each correct, -0.5 for each incorrect, minimum 0
        raw_score = correct_selected - (incorrect_selected * 0.5)
        score = max(0, raw_score) / total_correct

        is_perfect = user_set == correct_set
        has_partial = score > 0 and not is_perfect

        return {
            'is_correct': is_perfect,
            'score': min(1.0, score),  # Cap at 1.0
            'partial_credit': has_partial,
            'correct_selected': correct_selected,
            'incorrect_selected': incorrect_selected,
            'total_correct': total_correct
        }

def initialize_quiz_session():
    """Initialize a new quiz session with shuffled questions"""
    questions = load_questions()
    random.shuffle(questions)

    # Store shuffled question IDs in session
    session['quiz_questions'] = [q['id'] for q in questions]
    session['current_question_index'] = 0
    session['quiz_active'] = True

    return questions

def get_current_question():
    """Get the current question based on session state"""
    if 'quiz_questions' not in session or 'current_question_index' not in session:
        return None

    questions = load_questions()
    question_ids = session['quiz_questions']
    current_index = session['current_question_index']

    if current_index >= len(question_ids):
        return None

    current_question_id = question_ids[current_index]
    current_question = next((q for q in questions if q['id'] == current_question_id), None)

    return current_question

def generate_flashcard_id():
    """Generate unique ID for new flashcard"""
    flashcards = load_flashcards()
    if not flashcards:
        return 1
    return max(card['id'] for card in flashcards) + 1

def get_flashcard_categories():
    """Get all unique categories from flashcards"""
    flashcards = load_flashcards()
    categories = set()
    for card in flashcards:
        if card.get('category'):
            categories.add(card['category'])
    return sorted(list(categories))

def update_flashcard_progress(username, card_id, difficulty):
    """Update progress for a specific flashcard"""
    progress = load_flashcard_progress(username)
    today = datetime.now().strftime('%Y-%m-%d')

    # Initialize progress structure
    if 'studied_today' not in progress:
        progress['studied_today'] = []
    if 'card_stats' not in progress:
        progress['card_stats'] = {}

    # Update card statistics
    card_stats = progress['card_stats'].get(str(card_id), {
        'times_studied': 0,
        'difficulty_ratings': [],
        'last_studied': None
    })

    card_stats['times_studied'] += 1
    card_stats['difficulty_ratings'].append(difficulty)
    card_stats['last_studied'] = today

    # Keep only last 10 difficulty ratings
    if len(card_stats['difficulty_ratings']) > 10:
        card_stats['difficulty_ratings'] = card_stats['difficulty_ratings'][-10:]

    progress['card_stats'][str(card_id)] = card_stats

    # Add to today's studied cards if not already there
    if card_id not in progress['studied_today']:
        progress['studied_today'].append(card_id)

    save_flashcard_progress_data(username, progress)

def get_flashcard_stats(username):
    """Get comprehensive flashcard statistics for user"""
    flashcards = load_flashcards()
    user_progress = load_flashcard_progress(username)
    card_stats = user_progress.get('card_stats', {})

    stats = {
        'total_cards': len(flashcards),
        'studied_cards': len(card_stats),
        'unstudied_cards': len(flashcards) - len(card_stats),
        'due_cards': 0,
        'mastered_cards': 0,
        'learning_cards': 0,
        'difficult_cards': 0,
        'accuracy_rate': 0,
        'categories': {}
    }

    total_studies = 0
    hard_ratings = 0

    for card in flashcards:
        card_id = str(card['id'])
        card_progress = card_stats.get(card_id, {})
        category = card.get('category', 'General')

        # Initialize category stats
        if category not in stats['categories']:
            stats['categories'][category] = {
                'total': 0,
                'studied': 0,
                'mastered': 0
            }

        stats['categories'][category]['total'] += 1

        if card_id in card_stats:
            stats['categories'][category]['studied'] += 1

            times_studied = card_progress.get('times_studied', 0)
            recent_ratings = card_progress.get('difficulty_ratings', [])[-3:]  # Last 3 ratings

            total_studies += times_studied
            hard_ratings += sum(1 for r in recent_ratings if r == 'hard')

            # Categorize by performance
            if recent_ratings:
                avg_difficulty = sum(1 if d == 'hard' else 2 if d == 'medium' else 3 for d in recent_ratings) / len(recent_ratings)
                if avg_difficulty >= 2.5:  # Mostly easy/medium
                    stats['mastered_cards'] += 1
                    stats['categories'][category]['mastered'] += 1
                elif avg_difficulty >= 1.5:  # Mixed
                    stats['learning_cards'] += 1
                else:  # Mostly hard
                    stats['difficult_cards'] += 1
            else:
                stats['learning_cards'] += 1

    # Calculate accuracy rate (inverse of difficulty)
    if total_studies > 0:
        stats['accuracy_rate'] = max(0, 100 - (hard_ratings / total_studies * 100))

    return stats

def get_next_flashcard(username):
    """Get next flashcard using spaced repetition algorithm"""
    flashcards = load_flashcards()
    if not flashcards:
        return None

    progress = load_flashcard_progress(username)
    card_stats = progress.get('card_stats', {})

    # Score cards based on difficulty and study frequency
    scored_cards = []
    for card in flashcards:
        card_id = str(card['id'])
        stats = card_stats.get(card_id, {})

        # Calculate priority score
        times_studied = stats.get('times_studied', 0)
        recent_ratings = stats.get('difficulty_ratings', [])[-3:]  # Last 3 ratings

        # Higher score = higher priority
        score = 100  # Base score

        # Reduce score based on times studied (recently studied = lower priority)
        score -= times_studied * 10

        # Increase score for hard cards
        if recent_ratings:
            avg_difficulty = sum(1 if d == 'hard' else 2 if d == 'medium' else 3 for d in recent_ratings) / len(recent_ratings)
            score += (3 - avg_difficulty) * 20  # Hard cards get higher score

        # Add some randomness
        score += random.randint(-10, 10)

        scored_cards.append((score, card))

    # Sort by score (highest first) and return top card
    scored_cards.sort(key=lambda x: x[0], reverse=True)
    return scored_cards[0][1] if scored_cards else None

def clear_study_session(username):
    """Clear today's study session"""
    progress = load_flashcard_progress(username)
    progress['studied_today'] = []
    save_flashcard_progress_data(username, progress)

# ======================= INITIALIZE DATA FILES =======================

# Sample questions data structure
QUESTIONS = [
    {
        "id": 1,
        "question": "Which AWS service is primarily used for storing static files?",
        "options": ["EC2", "S3", "DynamoDB", "RDS"],
        "correct_answer": "S3",
        "explanation": "Amazon S3 (Simple Storage Service) is an object storage service that offers industry-leading scalability, data availability, security, and performance for storing static files."
    },
    {
        "id": 2,
        "question": "Which AWS service would you use to run containers?",
        "options": ["EC2", "S3", "ECS/EKS", "Lambda"],
        "correct_answer": "ECS/EKS",
        "explanation": "Amazon ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service) are services designed specifically for running containers in AWS."
    }
]

# Initialize all JSON files if they don't exist
if not os.path.exists('questions.json'):
    SimpleDataHelper.save_json('questions.json', QUESTIONS)

if not os.path.exists('progress.json'):
    SimpleDataHelper.save_json('progress.json', {})

if not os.path.exists('flashcards.json'):
    SimpleDataHelper.save_json('flashcards.json', [])

if not os.path.exists('flashcard_progress.json'):
    SimpleDataHelper.save_json('flashcard_progress.json', {})

if not os.path.exists('users.json'):
    SimpleDataHelper.save_json('users.json', {"admin": "password"})  # Default user

# ======================= AUTHENTICATION ROUTES =======================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        if username in users and users[username] == password:
            session['username'] = username
            flash(f'Welcome back, {username}!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    session.pop('username', None)
    # Clear quiz session data
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('quiz_active', None)
    flash(f'You have been logged out. Goodbye!')
    return redirect(url_for('login'))

@app.route('/reset_progress', methods=['POST'])
@login_required
def reset_progress():
    """Reset progress for the current user"""
    username = session.get('username')
    progress = load_progress()

    # Remove user's progress
    if username in progress:
        del progress[username]
        save_progress(progress)
        flash('Your progress has been reset successfully!')
    else:
        flash('No progress found to reset.')

    return jsonify({'success': True})

# ======================= MAIN ROUTES =======================

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/question_stats')
@login_required
def question_stats():
    """Return the total number of questions and user progress for progress tracking"""
    questions = load_questions()
    username = session.get('username')
    user_progress = get_user_progress(username)

    return jsonify({
        'total': len(questions),
        'ids': [q['id'] for q in questions],
        'completed': len(user_progress),
        'progress': user_progress
    })

# ======================= QUIZ ROUTES =======================

@app.route('/quiz')
@login_required
def quiz():
    """Redirect to quiz start - maintains backward compatibility"""
    return redirect(url_for('quiz_start'))

@app.route('/quiz/start')
@login_required
def quiz_start():
    """Start a new quiz session"""
    # Clear any existing quiz session
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('quiz_active', None)

    # Initialize new quiz
    initialize_quiz_session()

    return redirect(url_for('quiz_question'))

@app.route('/quiz/question')
@login_required
def quiz_question():
    """Display the current question"""
    if 'quiz_questions' not in session:
        flash('Please start the quiz first.')
        return redirect(url_for('quiz_start'))

    current_question = get_current_question()

    if current_question is None:
        # Quiz completed
        return redirect(url_for('quiz_complete'))

    # Convert markdown to HTML
    current_question['question_html'] = convert_markdown(current_question['question'])
    current_question['explanation_html'] = convert_markdown(current_question['explanation'])

    # Get user progress for this question
    username = session.get('username')
    user_progress = get_user_progress(username)
    question_id = str(current_question['id'])

    if question_id in user_progress:
        current_question['completed'] = True
        current_question['user_correct'] = user_progress[question_id]['correct']
    else:
        current_question['completed'] = False
        current_question['user_correct'] = False

    # Calculate progress
    current_index = session['current_question_index']
    total_questions = len(session['quiz_questions'])

    quiz_info = {
        'current_number': current_index + 1,
        'total_questions': total_questions,
        'progress_percentage': ((current_index + 1) / total_questions) * 100
    }

    return render_template('quiz.html',
                          question=current_question,
                          quiz_info=quiz_info,
                          single_question=True)

@app.route('/quiz/complete')
@login_required
def quiz_complete():
    """Show quiz completion summary"""
    if 'quiz_questions' not in session:
        flash('No quiz session found.')
        return redirect(url_for('index'))

    username = session.get('username')
    user_progress = get_user_progress(username)
    question_ids = session['quiz_questions']

    # Calculate results with score support
    total_questions = len(question_ids)
    answered_questions = 0
    correct_answers = 0
    total_score = 0.0

    for question_id in question_ids:
        if str(question_id) in user_progress:
            answered_questions += 1
            if user_progress[str(question_id)]['correct']:
                correct_answers += 1
            # Add score if available (for partial credit)
            score = user_progress[str(question_id)].get('score', 1.0 if user_progress[str(question_id)]['correct'] else 0.0)
            total_score += score

    results = {
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'total_score': total_score,
        'score_percentage': (correct_answers / total_questions * 100) if total_questions > 0 else 0,
        'weighted_score_percentage': (total_score / total_questions * 100) if total_questions > 0 else 0
    }

    # Clear quiz session
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('quiz_active', None)

    return render_template('quiz_complete.html', results=results)

@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    question_id = int(request.form.get('question_id'))
    username = session.get('username')

    questions = load_questions()
    question = next((q for q in questions if q['id'] == question_id), None)

    if not question:
        flash('Question not found.')
        return redirect(url_for('quiz'))

    # Get question type and correct answers (with backward compatibility)
    question_type = question.get('question_type', 'single')
    correct_answers = question.get('correct_answers', [question.get('correct_answer', '')])

    # Handle backward compatibility - if correct_answers doesn't exist but correct_answer does
    if not correct_answers and question.get('correct_answer'):
        correct_answers = [question.get('correct_answer')]

    # Get user answers
    if question_type == 'multiple':
        # Multiple choice - get all checked answers
        user_answers = request.form.getlist('answer')
    else:
        # Single choice - get single answer
        user_answer = request.form.get('answer')
        user_answers = [user_answer] if user_answer else []

    # Check answers and calculate score
    result = check_user_answer(user_answers, correct_answers, question_type)

    # Convert markdown to HTML
    question['question_html'] = convert_markdown(question['question'])
    question['explanation_html'] = convert_markdown(question['explanation'])

    # Save user progress (use score for more nuanced tracking)
    save_user_progress(username, question_id, result['is_correct'], result['score'])

    return render_template('result.html',
                          question=question,
                          user_answers=user_answers,
                          correct_answers=correct_answers,
                          result=result,
                          question_type=question_type)

@app.route('/quiz/next', methods=['POST'])
@login_required
def quiz_next():
    """Move to next question"""
    if 'current_question_index' in session:
        session['current_question_index'] += 1

    return redirect(url_for('quiz_question'))

# ======================= QUESTION MANAGEMENT ROUTES =======================

@app.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        questions = load_questions()

        # Generate new ID (max ID + 1)
        new_id = max([q['id'] for q in questions], default=0) + 1

        # Get form data
        question_text = request.form.get('question')
        question_type = request.form.get('question_type', 'single')

        # Get options (filter out empty ones)
        options = []
        for i in range(1, 7):
            option = request.form.get(f'option{i}')
            if option and option.strip():
                options.append(option.strip())

        # Process correct answers based on question type
        correct_answers = process_question_answers(request.form)
        explanation = request.form.get('explanation')

        # Validate that we have at least 2 options and at least 1 correct answer
        if len(options) < 2:
            flash('Please provide at least 2 answer options.')
            return render_template('add_question.html')

        if not correct_answers:
            flash('Please select at least one correct answer.')
            return render_template('add_question.html')

        # Validate that all correct answers exist in options
        for correct in correct_answers:
            if correct not in options:
                flash(f'Correct answer "{correct}" must match one of the provided options exactly.')
                return render_template('add_question.html')

        # Create new question with backward compatibility
        new_question = {
            "id": new_id,
            "question": question_text,
            "options": options,
            "question_type": question_type,
            "correct_answers": correct_answers,
            # Keep old format for backward compatibility
            "correct_answer": correct_answers[0] if correct_answers else "",
            "explanation": explanation
        }

        # Add to questions list
        questions.append(new_question)
        save_questions(questions)

        flash('Question added successfully!')
        return redirect(url_for('add_question'))

    return render_template('add_question.html')

@app.route('/manage_questions')
@login_required
def manage_questions():
    questions = load_questions()
    return render_template('manage_questions.html', questions=questions)

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    questions = load_questions()
    question = next((q for q in questions if q['id'] == question_id), None)

    if question is None:
        flash('Question not found!')
        return redirect(url_for('manage_questions'))

    if request.method == 'POST':
        # Get form data
        question_text = request.form.get('question')
        question_type = request.form.get('question_type', question.get('question_type', 'single'))

        # Get options (filter out empty ones)
        options = []
        for i in range(1, 7):
            option = request.form.get(f'option{i}')
            if option and option.strip():
                options.append(option.strip())

        # Process correct answers based on question type
        correct_answers = process_question_answers(request.form)
        explanation = request.form.get('explanation')

        # Validate
        if len(options) < 2:
            flash('Please provide at least 2 answer options.')
            return render_template('edit_question.html', question=question)

        if not correct_answers:
            flash('Please select at least one correct answer.')
            return render_template('edit_question.html', question=question)

        # Update question data with backward compatibility
        question['question'] = question_text
        question['options'] = options
        question['question_type'] = question_type
        question['correct_answers'] = correct_answers
        question['correct_answer'] = correct_answers[0] if correct_answers else ""
        question['explanation'] = explanation

        save_questions(questions)
        flash('Question updated successfully!')
        return redirect(url_for('manage_questions'))

    return render_template('edit_question.html', question=question)

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    questions = load_questions()
    questions = [q for q in questions if q['id'] != question_id]
    save_questions(questions)
    flash('Question deleted successfully!')
    return redirect(url_for('manage_questions'))

# ======================= FLASHCARD ROUTES =======================

@app.route('/flashcards')
@login_required
def flashcards():
    """Display all flashcards with management options"""
    flashcards = load_flashcards()
    categories = get_flashcard_categories()
    username = session.get('username')

    # Get filter parameters
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')

    # Filter flashcards
    filtered_cards = flashcards
    if category_filter:
        filtered_cards = [card for card in filtered_cards if card.get('category') == category_filter]
    if search_query:
        filtered_cards = [card for card in filtered_cards
                         if search_query.lower() in card.get('front', '').lower() or
                            search_query.lower() in card.get('back', '').lower()]

    # Generate stats for the template
    stats = get_flashcard_stats(username)

    # Add progress info to each flashcard
    user_progress = load_flashcard_progress(username)
    card_stats = user_progress.get('card_stats', {})
    for card in filtered_cards:
        card_id = str(card['id'])
        card['progress'] = card_stats.get(card_id, {})

    return render_template('flashcards.html',
                         flashcards=filtered_cards,
                         categories=categories,
                         current_category=category_filter,
                         search_query=search_query,
                         stats=stats)

@app.route('/flashcards/add', methods=['GET', 'POST'])
@login_required
def add_flashcard():
    """Add a new flashcard"""
    if request.method == 'POST':
        front = request.form.get('front')
        back = request.form.get('back')
        category = request.form.get('category', 'General')
        tags = request.form.get('tags', '')

        if not front or not back:
            flash('Both front and back content are required!', 'error')
            return render_template('add_flashcard.html')

        # Load existing flashcards
        flashcards = load_flashcards()

        # Create new flashcard
        new_card = {
            'id': generate_flashcard_id(),
            'front': front,
            'back': back,
            'category': category,
            'tags': [tag.strip() for tag in tags.split(',') if tag.strip()],
            'created_date': datetime.now().isoformat(),
            'difficulty': 'medium',
            'times_studied': 0,
            'last_studied': None
        }

        flashcards.append(new_card)
        save_flashcards(flashcards)

        flash('Flashcard added successfully!', 'success')
        return redirect(url_for('flashcards'))

    return render_template('add_flashcard.html')

@app.route('/flashcards/edit/<int:card_id>', methods=['GET', 'POST'])
@login_required
def edit_flashcard(card_id):
    """Edit an existing flashcard"""
    flashcards = load_flashcards()
    card = next((card for card in flashcards if card['id'] == card_id), None)

    if not card:
        flash('Flashcard not found!', 'error')
        return redirect(url_for('flashcards'))

    if request.method == 'POST':
        card['front'] = request.form.get('front')
        card['back'] = request.form.get('back')
        card['category'] = request.form.get('category', 'General')
        card['tags'] = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]

        save_flashcards(flashcards)
        flash('Flashcard updated successfully!', 'success')
        return redirect(url_for('flashcards'))

    return render_template('edit_flashcard.html', card=card)

@app.route('/flashcards/delete/<int:card_id>', methods=['POST'])
@login_required
def delete_flashcard(card_id):
    """Delete a flashcard"""
    flashcards = load_flashcards()
    flashcards = [card for card in flashcards if card['id'] != card_id]
    save_flashcards(flashcards)

    flash('Flashcard deleted successfully!', 'success')
    return redirect(url_for('flashcards'))

@app.route('/flashcards/study/card', methods=['GET', 'POST'])
@login_required
def study_card():
    """Study flashcards with spaced repetition"""
    username = session['username']

    # Handle POST requests (rating cards, skipping)
    if request.method == 'POST':
        action = request.form.get('action')
        card_id = request.form.get('card_id')

        if action == 'rate' and card_id:
            difficulty = request.form.get('difficulty')
            update_flashcard_progress(username, int(card_id), difficulty)

        # Redirect to show next card
        return redirect(url_for('study_card'))

    # Handle restart parameter
    if request.args.get('restart'):
        clear_study_session(username)

    # Get next card to study
    current_card = get_next_flashcard(username)

    if current_card:
        # Calculate progress
        total_cards = len(load_flashcards())
        progress_data = load_flashcard_progress(username)
        cards_studied = len(progress_data.get('studied_today', []))
        progress = (cards_studied / total_cards * 100) if total_cards > 0 else 0

        return render_template('study_flashcards.html',
                             current_card=current_card,
                             progress=progress,
                             cards_studied=cards_studied,
                             total_cards=total_cards)
    else:
        # No more cards to study
        return render_template('study_flashcards.html',
                             current_card=None,
                             progress=100,
                             cards_studied=0,
                             total_cards=0)

@app.route('/flashcards/study')
@login_required
def study_flashcards():
    """Start a flashcard study session - redirects to study card"""
    return redirect(url_for('study_card'))

@app.route('/flashcards/study/start')
@login_required
def start_study_session():
    """Start a new study session and clear previous session"""
    username = session.get('username')
    clear_study_session(username)
    return redirect(url_for('study_card'))

# ======================= UTILITY ROUTES =======================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files directly"""
    return send_from_directory('static', filename)

@app.route('/markdown_preview', methods=['POST'])
@login_required
def markdown_preview():
    """API endpoint for previewing markdown"""
    text = request.form.get('text', '')
    html = convert_markdown(text)
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5019, debug=False)  # Set debug=False for production


# David This is test
