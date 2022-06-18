import os, sys
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
   
    @app.route('/categories', methods = ['GET'])
    def get_categories():
        categories = Category.query.all()
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

    @app.route('/questions',methods = ['POST'])
    def new_question():
        body = request.get_json()

        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search_term))
            ).all()

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


    @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
    def get_categorized_questions(category_id):

        #category = Category.query.filter_by(id=id).one_or_none()

        #if (category is None):
            #abort(400)
        # if category_id!=0:
        #     selection = (Question.query.filter(Question.category == category_id)
        #     .order_by(Question.id)
        #     .all())
        # else:
        #     selection = (Question.query.order_by(Question.id).all())
            
        # paginated_questions = paginate_questions(request,selection)

        # if not paginated_questions:
        #     abort(404)

        # return jsonify({
        #     'success':True,
        #     'categorized_questions':paginated_questions,
        #     'total_Questions':len(selection),
        #     'current_category': category_id
        # })
        try: 
            page = request.args.get('page',1, type = int)
            questions = (Question.query
            .order_by(Question.id)
            .filter(Question.category == category_id)
            .paginate(page= page, per_page = QUESTIONS_PER_PAGE))

            formatted_questions = [
                question.format() for question in questions.items
            ]
            if len(formatted_questions) == 0:
                abort(404)
            else:
                return jsonify({
                    'success': True,
                    'questions':formatted_questions,
                    'total_questions':questions.total,
                    'current_category':category_id
                })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        
        #Retrieve JSON data
        previous_questions = body.get('previous_questions', None)
        current_category = body.get('quiz_category', None)

        #Play quiz with no previous questions
        if ((current_category is None) or (previous_questions is None)):
             abort(400)

        # load questions all questions if "ALL" is selected
        if (current_category['id'] == 0):
            questions = Question.query.all()
        # load questions for given category
        else:
            questions = Question.query.filter_by(category=current_category['id']).all()

        # get total number of questions
        total = len(questions)

        # picks a random question
        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        # checks to see if question has already been used
        def check_if_used(question):
            used = False
            for q in previous_questions:
                if (q == question.id):
                    used = True

            return used

        # get random question
        question = get_random_question()

        # check if used, execute until unused question found
        while (check_if_used(question)):
            question = get_random_question()

            # if all questions have been tried, return without question
            # necessary if category has <5 questions
            if (len(previous_questions) == total):
                return jsonify({
                    'success': True
                })

        # return the question
        return jsonify({
            'success': True,
            'question': question.format()
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success':False,
            'error':422,
            'message':'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error':400,
            'message':'bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
         return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405

    return app

