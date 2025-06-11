import json
import urllib.request

from logger import get_logger

from flask import Blueprint, request, jsonify
import httpx
from load_services import ServicesLoaderSingleton

from flask import Flask, request, jsonify
import requests
from utils import requires_auth

app_bp = Blueprint('app', __name__)
s = ServicesLoaderSingleton()
logger = get_logger("gateway_logger")


def forward_request(service_url):
    """Forward the request to the appropriate microservice."""
    headers = dict(request.headers)
    headers.pop('Host', None)
    path = f'/{"/".join(request.path.split("/")[3:])}'
    response = []
    logger.info("-"*100)
    logger.info(f"Request Method:{request.method}")
    logger.info(f"URL: {service_url + path}")
    logger.info("-" * 100)
    try:
        if request.method == 'GET':
            response = requests.request(
                method=request.method,
                url=service_url + path,
                headers=headers,
                params=request.args,
            )
        if request.method == 'POST':
            # Extract form fields
            form_data = request.form.to_dict()
            # Extract files (Read files properly)
            files = {
                key: (file.filename, file.read(), file.mimetype)
                for key, file in request.files.items()
            }

            # Forward the request using httpx (Synchronous)
            with httpx.Client() as client:
                response = client.post(
                    url=f"{service_url}{path}",
                    params=request.args,
                    headers=request.headers,
                    data=form_data,  # Send form fields
                    files=files,  # Send uploaded files
                )

            # response = requests.request(
            #     method=request.method,
            #     url=service_url + path,
            #     headers=headers,
            #     params=request.args,
            #     data=form_data,
            #     files=files
            # )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


@app_bp.route("<service_route>/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
@requires_auth(logger_instance=logger)
def services(service_route, path):
    for service in s.get_json_as_list():
        if service_route == service["slug"]:
            return forward_request(service["redirect_url"])
    return jsonify({"error": "invalid url"})
