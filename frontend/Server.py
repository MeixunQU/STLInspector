# pylint: disable=invalid-name

from flask import Flask, render_template, abort, Response, request, Markup, send_from_directory
from flask_assets import Bundle, Environment
from os.path import join, realpath, dirname
from os import sys, path
# Make the core module available
sys.path.append(join(dirname(dirname(path.abspath(__file__))), 'core'))
from .ProjectList import ProjectList
import json
import markdown

def exceptionHandler(e):
    print(e)
    import sys, traceback
    print "Exception in user code:"
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60

def run():
    app = Flask(__name__)

    datapath = realpath(join(realpath(dirname(__file__)), '../data'))
    """data path where the files are located"""

    projectList = ProjectList(datapath)
    """interface to the projects and backend"""

    """
    Bundle the javascript files into one distribution file
    """
    bundles = {
        'STLInspector_js': Bundle(
            'js/AlertView.js',
            'js/BooleanChart.js',
            'js/Project.js',
            'js/Projects.js',
            'js/ProjectsView.js',
            'js/ProjectView.js',
            'js/RealChart.js',
            'js/ServerRequest.js',
            'js/SignalView.js',
            'js/STLInspector.js',
            output='build/STLInspector.js'),
    }
    assets = Environment(app)
    assets.register(bundles)

    @app.route("/")
    def index():
        """index page loader

        loads and renders the index template
        """
        return render_template('index.html')

    @app.route("/documentation/")
    def documentation():
        """renders the documentation page"""
        fdoc = open(join(dirname(dirname(__file__)), "doc/documentation.md"), "r")
        doc = markdown.Markdown(extensions=['mdx_math'], extension_configs={'mdx_math': {'enable_dollar_delimiter': True}}).convert(fdoc.read())
        fdoc.close()
        return render_template('documentation.html', doctext=Markup(doc))

    @app.route('/documentation/images/<path:filename>')
    def documentation_images(filename):
        return send_from_directory('../doc/images', filename)

    @app.route("/api/projects/list", methods=['POST'])
    def api_projects_list():
        """project list loader"""

        try:
            return Response(
                json.dumps(projectList.list()),
                mimetype='application/json'
                )
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/projects/create", methods=['POST'])
    def api_projects_create():
        """create a project with given name"""

        try:
            projectTitle = request.form['title']
            return Response(
                json.dumps(projectList.create(projectTitle)),
                mimetype='application/json'
                )
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/projects/delete", methods=['POST'])
    def api_projects_delete():
        """deletes the project file"""

        try:
            projectId = request.form['id']
            projectList.delete(projectId)
            return Response('true', mimetype='application/json')
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/project/save", methods=['POST'])
    def api_project_save():
        """saves the project to file"""

        try:
            projectId = request.form['id']
            projectList.saveProject(projectId)
            return Response('true', mimetype='application/json')
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/project/close", methods=['POST'])
    def api_project_close():
        """is called when a project is closed in the frontend"""

        try:
            projectId = request.form['id']
            projectList.close(projectId)
            return Response('true', mimetype='application/json')
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/project/load", methods=['POST'])
    def api_project_load():
        """returns the data of a project with the given id"""

        try:
            projectId = request.form['id']
            project = projectList.project(projectId)
            return Response(
                json.dumps(project.state()),
                mimetype='application/json'
                )
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/project/change", methods=['POST'])
    def api_project_change():
        """changes project variables"""

        try:
            projectId = request.form['id']
            project = projectList.project(projectId)
            if 'stlCandidate' in request.form:
                project.setStlCandidate(request.form['stlCandidate'])
            if 'textRequirement' in request.form:
                project.setTextRequirement(request.form['textRequirement'])
            if 'textNotes' in request.form:
                project.setTextNotes(request.form['textNotes'])
            return Response('true', mimetype='application/json')
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/project/test", methods=['POST'])
    def api_project_test():
        """returns an existing or new test signal"""

        try:
            projectId = request.form['id']
            test_type = request.form['type']
            parameter = request.form['parameter']
            project = projectList.project(projectId)
            if test_type == 'evaluate':
                test = project.testForName(parameter)
            else:
                test = project.testById(int(parameter))
            return Response(json.dumps(test), mimetype='application/json')
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    @app.route("/api/project/testEvaluation", methods=['POST'])
    def api_project_testEvaluation():
        """returns an existing or new test signal"""

        try:
            projectId = request.form['id']
            testId = int(request.form['testId'])
            username = request.form['username']
            evaluation = request.form['evaluation'] == 'true'
            project = projectList.project(projectId)
            project.setTestEvaluation(
                testId,
                username,
                evaluation
                )
            return Response('true', mimetype='application/json')
        except Exception as e:
            exceptionHandler(e)
            abort(500)

    app.run(debug=False)
