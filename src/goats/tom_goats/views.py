import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from tom_alerts.models import BrokerQuery
from datetime import datetime
from typing import Any


@csrf_exempt
def receive_query(request):
    """Receive a query string or JSON object and print it to the terminal.

    Parameters
    ----------
    request : `HttpRequest`
        The HTTP request object.

    Returns
    -------
    JsonResponse
        A JSON response indicating success or failure.
    """
    query_data = request.body.decode("utf-8")

    # View the available alert classes.
    # print(get_service_classes())

    if query_data:
        try:
            # Attempt to parse the query data as JSON
            parsed_query = json.loads(query_data)
            print("Received JSON Query:", parsed_query)
        except json.JSONDecodeError:
            return HttpResponse(status=400)  # Bad request.

        # Create a new BrokerQuery instance with the necessary data
        broker_query = BrokerQuery.objects.create(
            name=_generate_query_name(parsed_query),
            broker='ANTARES',
            parameters=parsed_query,  # Assuming parsed_query contains the necessary parameters
        )

        # Save the new BrokerQuery instance to the database
        broker_query.save()

        return HttpResponse(status=204)


def _generate_query_name(data_dict: dict[str, Any]) -> str:
    """Generates a unique name based on the presence of "locus_id" or
    "esquery" in the input dictionary.

    Parameters
    ----------
    data_dict : `dict`
        The input dictionary containing the data.

    Returns
    -------
    `str`
        A unique name generated based on the input data.

    Raises
    ------
    NotImplementedError
        Raised if the query is not supported.
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    if "locusid" in data_dict:
        name = f"{data_dict['locusid']}_{timestamp}"
    elif "esquery" in data_dict:
        name = f"esquery_{timestamp}"
    else:
        raise NotImplementedError("Extension query not supported.")

    return name
