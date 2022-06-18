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
   
    @app.route('/categories',methods = ['GET'])
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


    @app.route('/categories/<int:id>/questions', methods = ['GET'])
    def get_categorized_questions(id):

        category = Category.query.filter_by(id=id).one_or_none()

        if (category is None):
            abort(400)

        selection = Question.query.filter_by(category=category.id).all()
        paginated_questions = paginate_questions(request,selection)

        return jsonify({
            'success':True,
            'categorized_questions':paginated_questions,
            'total_Questions':len(Question.query.all()),
            'current_category':category.type
        })


    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        if not body:
            abort(400)
        
        #Retrieve JSON data
        previous_questions = body.get('previous_questions', None)
        current_category = body.get('quiz_category', None)

        #Play quiz with no previous questions
        if not previous_questions:
            if current_category and current_category['id']!=0:
                quiz_questions = (Question.query
                    .filter(Question.category == str(current_category['id']))
                    .all())
            else:
                quiz_questions = (Question.query.all())
        #Filter previous questions and play
        else:
            if current_category and current_category['id']!=0:
                quiz_questions = (Question.query
                    .filter(Question.category == str(current_category['id']))
                    .filter(Question.id.notin_(previous_questions))
                    .all())
            #Play quiz with no given category(play all)
            else:
                quiz_questions = (Question.query
                    .filter(Question.id.notin_(previous_questions))
                    .all())
    
    # Format questions & get a random question
        questions_formatted = [question.format() for question in quiz_questions]
        quiz = questions_formatted[random.randint(0, len(questions_formatted)-1)]
    
        return jsonify({
            'success': True,
            'question': quiz
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

