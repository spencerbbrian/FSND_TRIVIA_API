import os, unittest, json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASS')
        self.database_path = "postgresql://{}:{}@{}/{}".format(
        db_user, db_password, "localhost:5432", self.database_name)
        setup_db(self.app,self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_invalid_page(self):
        res = self.client().get('/quest',json ={'category':'Science'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories'])>0)
    
    def test_error_method_for_categories(self):
        res = self.client().post('/categories', json={'type':'fiction'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method not allowed')

    def test_get_all_question(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories'])>0)

    def test_error_methods_for_questions(self):
        res = self.client().patch('/questions', json={'type':'fiction'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method not allowed')

    def test_error_get_questions(self):
        res = self.client().get('/questions?page=15')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')
        
    def test_new_question(self):
        json_question = {
            'question':'Will I complete this project?',
            'answer':'Yes',
            'category':'5',
            'difficulty': 5
        }
        res = self.client().post('/questions', json = json_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question_created'])
        self.assertTrue(data['total_questions'])

    def test_error_delete_invalid_question(self):
        res = self.client().delete('/questions/25000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'unprocessable')

    def test_delete_question(self):
        res = self.client().delete('/questions/22')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'],22)

    def test_new_search(self):
        search_term = {
            'searchTerm': 'heaviest'
        }
        res= self.client().post('/questions', json = search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
    
    def test_invalid_search_term(self):
        search_term = {
            'searchTerm':'fling'
        }
        res = self.client().post('/questions',json = search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'resource not found')

    def test_get_categorized_questions(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_Questions'])
        self.assertTrue(data['current_category'])
    
    def test_error_get_invalid_category_questions(self):
        res = self.client().get('/categories/20000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'bad request')

    def test_error_invalid_method_category_questions(self):
        res = self.client().patch('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method not allowed')

    def test_play_quiz(self):
        json_data = {
            'previous_questions' : [15,8,21],
            'quiz_category':{'id' : '3', 'type':'Science'}
        }
        res = self.client().post('/quizzes', json = json_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] not in json_data['previous_questions'])
    
    def test_error_play_quiz_no_json_data(self):
        res = self.client().post('/quizzes',json = {})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'bad request')
    
    def test_error_play_quiz_bad_method(self):
        json_data = {
            'previous_questions' : [15,8,21],
            'quiz_category':{'id' : '3', 'type':'Science'}
        }
        res = self.client().patch('/quizzes', json = json_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()