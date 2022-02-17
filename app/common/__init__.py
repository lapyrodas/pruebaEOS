from  flask import Flask, jsonify, url_for
from flask_restful import Api,Resource

from app.common.error_handling import AppErrorBaseClass,ObjectNotFound
from  app.eos.resources import CatalogList,DownloadScene


def prefix_route(route_function, prefix='', mask='{0}{1}'):
  '''
    Defines a new route function with a prefix.
    The mask argument is a `format string` formatted with, in that order:
      prefix, route
  '''
  def newroute(route, *args, **kwargs):
    '''New function to prefix the route'''
    return route_function(mask.format(prefix, route), *args, **kwargs)
  return newroute

def create_app(settings_module):
    app = Flask(__name__)
    app.config.from_object(settings_module)
    app.debug = True
    app.route = prefix_route(app.route, '/pruebaeos')
    # Inicializa las extensiones
    #   ma.init_app(app)
    # Captura todos los errores 404
    # Deshabilita el modo estricto de acabado de una URL con /
    app.url_map.strict_slashes = False
    # Registra manejadores de errores personalizados
    register_error_handlers(app)
    @app.route('/')
    def index():
        return("indexpage")

    api = Api(app,prefix='/pruebaeos')
    api.add_resource(CatalogList, '/catalogo')
    api.add_resource(DownloadScene, '/descarga')
    Api(app, catch_all_404s=True)
    return app

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception_error(e):
        return jsonify({'msg': 'Internal server error',"error":e}), 500
    @app.errorhandler(405)
    def handle_405_error(e):
        return jsonify({'msg': 'Method not allowed'}), 405
    @app.errorhandler(403)
    def handle_403_error(e):
        return jsonify({'msg': 'Forbidden error'}), 403
    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({'msg': 'Not Found error'}), 404
    @app.errorhandler(AppErrorBaseClass)
    def handle_app_base_error(e):
        return jsonify({'msg': str(e)}), 500
    @app.errorhandler(ObjectNotFound)
    def handle_object_not_found_error(e):
        return jsonify({'msg': str(e)}), 404