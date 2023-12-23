from flask import Flask, render_template
import logging
import axs

app = Flask(__name__)

class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return "/healthcheck" not in record.getMessage()

@app.route('/', methods=['GET'])
def axs_price():
    encoded_image = axs.main()
    plot_url = "data:image/png;base64," + encoded_image.decode()
    return render_template('index.html', plot_url=plot_url)


if __name__ == '__main__':
    logging.getLogger('werkzeug').addFilter(HealthCheckFilter())
    app.run(
        debug=True,
        host='0.0.0.0',
        port=52801)