from django.test import Client, client
from .models import Todo
from datetime import date
from itertools import repeat
from pipe import izip, select, where
from hypothesis import example, given, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework import status

"""
Current testing methodology uses property testing with hypothesis.
By stochastically and methodically fuzzing different test cases, we are able to
to cover a wide range of test cases.
"""


def get_client_default_list():
    """
    Generate a default list of data to be tested with
    """
    keys = [
        "id",
        "title",
        "description",
        "timestamp_creation",
        "timestamp_updated",
        "status",
    ]
    current_date = date.today()
    data = [
        [
            1,
            "Test case 1",
            "Testing description for first case",
            str(current_date),
            str(current_date),
            Todo.TodoStatus.NOT_COMPLETED.label,
        ],
        [
            2,
            "Test case 2",
            "Testing description for second case",
            str(current_date),
            str(current_date),
            Todo.TodoStatus.COMPLETED.label,
        ],
        [
            3,
            "Test case 3",
            "Testing description for third case",
            str(current_date),
            str(current_date),
            Todo.TodoStatus.COMPLETED.label,
        ],
    ]
    return keys, data


def check_params(title, desc, stat):
    """
    check_params
        Check if the parameters are in their intended form
    Parameters
    ----------
    title : str
        title of the new todo
    desc : str
        description of the new todo
    stat : str
        todo status of the new todo

    Returns
    -------
    bool
        check if the parameters are valid
    """
    return (
        len(title) > 100
        or len(desc) > 200
        or stat not in ["T", "F"]
        or len(title) == 0
        or len(desc) == 0
    )


# Create your tests here.
class TodoListTestCases(TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment for testing
        """
        Todo.objects.create(
            title="Test case 1",
            description="Testing description for first case",
            status=Todo.TodoStatus.NOT_COMPLETED,
        )

        Todo.objects.create(
            title="Test case 2",
            description="Testing description for second case",
            status=Todo.TodoStatus.COMPLETED,
        )

        Todo.objects.create(
            title="Test case 3",
            description="Testing description for third case",
            status=Todo.TodoStatus.COMPLETED,
        )

    def test_list_get(self):
        c = Client()
        response = c.get("/todo/api")
        keys, data = get_client_default_list()
        tested_data = (
            repeat(keys, 3) | izip(data) | select(lambda x: dict(x[0] | izip(x[1])))
        )  # repeat list of keys by 3, and zip them with each of the data
        # essentially creates a list of dictionaries between the keys and the data rows
        self.assertTrue(
            all(  # compare the response with the tested data
                response.data
                | select(lambda x: dict(**x))
                | izip(tested_data)
                | select(lambda x: x[0] == x[1])
            )
        )

    @given(
        st.text(),
        st.text(),
        st.text(),
    )
    @example("Test1", "Desc1", "F")
    @example("", "", "F")
    def test_list_post_all_data(self, title, description, stat):
        c = Client()
        response = c.post(
            "/todo/api",
            data={
                "description": description,
                "title": title,
                "status": stat,
            },
        )
        if check_params(
            title, description, stat
        ):  # if the data are illegal, we expect a 400 response
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            current_date = str(date.today())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data.get("title"), title)
            self.assertEqual(response.data.get("description"), description)
            self.assertEqual(
                response.data.get("status"), dict(Todo.TodoStatus.choices)[stat]
            )
            self.assertEqual(response.data.get("timestamp_creation"), current_date)
            self.assertEqual(response.data.get("timestamp_updated"), current_date)

    @given(st.integers(0, 5))
    @example(3)
    def test_get_specific_id(self, id) -> None:
        c = Client()
        response = c.get(f"/todo/api/{id}")

        if id not in [1, 2, 3]:  # if id does not exist, should return an error
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:  # otherwise we expect the data to not be modified
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            keys, data = get_client_default_list()
            stored_data = dict(keys | izip(next(data | where(lambda x: x[0] == id))))
            self.assertEqual(stored_data, response.data)

    @given(st.integers(0, 5), st.text(), st.text(), st.text())
    @example(2, "Test1", "Case1", "F")
    @example(1, "", "", "")
    @example(1, "", "0", "")
    @example(1, "", "", "0")
    @example(4, "", "", "0")
    def test_update_specific_id_all_data(self, id, title, description, stat):
        c = Client()
        data_input = {
            "title": title,
            "description": description,
            "status": stat,
        }
        response = c.put(
            f"/todo/api/{id}",
            data=data_input,
            content_type="application/json",  # Other types cause unsupported media errors. Unable to determine whether this is an issue with django or with something else.
        )
        # Check if the paramters are valid
        if id not in [1, 2, 3] or check_params(title, description, stat):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:  # Check if the modification was successfully achieved
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(  # Ensure the data where correctly modified
                all(
                    tuple(data_input.keys())
                    | select(
                        lambda k: (
                            response.data[k],
                            data_input[k]
                            if k is not "status"
                            else dict(Todo.TodoStatus.choices)[data_input[k]],
                        )
                    )
                )
            )
