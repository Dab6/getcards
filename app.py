from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API!"})

@app.route('/api/getdata', methods=['GET'])
def get_data():
    access_token = request.args.get('accessToken')
    proxy = request.args.get('proxy')  # Get the proxy from the URL parameters

    if not access_token:
        return jsonify({"error": "Access token is required"}), 400  # Bad Request if no token is provided

    if not proxy:
        return jsonify({"error": "Proxy is required"}), 400  # Bad Request if no proxy is provided

    url = os.getenv('API_URL')  # Get the URL from environment variable
    referer = os.getenv('REFERER')  # Get the Referer from environment variable

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'accessToken': access_token,  # Include the access token in the headers
        'Connection': 'keep-alive',
        'Referer': referer,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'If-None-Match': 'W/cf2-TqWDa+EvD6nexyBeysl55OTEwmQ',
        'TE': 'trailers'
    }

    # Define proxy settings
    proxies = {
        "http": proxy,
        "https": proxy
    }

    while True:
        try:
            # Make the request through the proxy
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()  # Raises HTTPError for 4xx and 5xx responses
            return jsonify(response.json())  # Return the JSON response from the API
        except requests.exceptions.HTTPError as err:
            app.logger.error(f"HTTPError: {err}, Response: {response.text}")  # Log the error
            return jsonify({"error": str(err), "response": response.text}), response.status_code
        except requests.exceptions.ProxyError as err:
            app.logger.error(f"ProxyError: {err}")  # Log the proxy error
            if "502 Bad Gateway" in str(err):
                app.logger.info("Proxy failed with 502 Bad Gateway, waiting for 10 seconds and retrying...")
                time.sleep(10)  # Wait for 10 seconds before retrying
                continue  # Retry the request
            return jsonify({"error": "Proxy connection failed", "details": str(err)}), 502  # Bad Gateway
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")  # Log any other exceptions
            return jsonify({"error": "An unexpected error occurred."}), 500  # Internal Server Error

if __name__ == "__main__":
    app.run(debug=True)
