from boac.factory import create_app

if __name__ == '__main__':
    app = create_app()
    app.logger.info('BOAC server running on http://%s:%s !', app.config['HOST'], app.config['PORT'])
    app.run(host=app.config['HOST'], port=app.config['PORT'])
