
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
    page = request.args.get('page',1,type = int)
    start = (page - 1 ) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/": {'origins': '*'}})


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
        'GET,POST,PUT,DELETE,OPTIONS')
        return response
   
    @app.route('/catgories',methods = ['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        
        if len(categories_dict) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories' : categories_dict
        })
    
    @app.route('/questions', methods =['GET'])
    def get_question():
        selection = Question.query.all()
        categories = Category.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request,selection)

        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions':current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })


    @app.route('/questions/<int:id>',methods = ['DELETE'])
    def delete_question(id):
        try:
            question =Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
            'success':True,
            'deleted': id,
            })

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions',methods = ['POST'])
    def new_question():
        body = request.get_json()

        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search_term))
            )

            if len(selection) == 0:
                abort(404)

            paginated_questions = paginate_questions(request,selection)

            return jsonify({
                'success':True,
                'questions': paginated_questions,
                'totalQuestions': len(Question.query.all())
            })
        
        else:
            new_question = body.get('question',None)
            new_answer = body.get('answer',None)
            new_difficulty = body.get('difficulty', None)
            new_category = body.get('category',None)

            if ((new_question is None) or (new_answer is None) 
                or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                question = Question(question=new_question, answer=new_answer,
                difficulty=new_difficulty,category=new_category)

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request,selection)

                return jsonify({
                    'success': True,
                    'question_id':question.id,
                    'question_created': question.question,
                    'question_category':question.category,
                    'questions': current_questions,
                    'total_questions':len(Question.query.all())
                })
            except:
                abort(422)



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

