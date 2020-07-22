# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.functions_v1.services.cloud_functions_service import (
    CloudFunctionsServiceAsyncClient,
)
from google.cloud.functions_v1.services.cloud_functions_service import (
    CloudFunctionsServiceClient,
)
from google.cloud.functions_v1.services.cloud_functions_service import pagers
from google.cloud.functions_v1.services.cloud_functions_service import transports
from google.cloud.functions_v1.types import functions
from google.cloud.functions_v1.types import functions as gcf_functions
from google.cloud.functions_v1.types import operations
from google.iam.v1 import iam_policy_pb2 as iam_policy  # type: ignore
from google.iam.v1 import options_pb2 as options  # type: ignore
from google.iam.v1 import policy_pb2 as policy  # type: ignore
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.type import expr_pb2 as expr  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert CloudFunctionsServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        CloudFunctionsServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        CloudFunctionsServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        CloudFunctionsServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        CloudFunctionsServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        CloudFunctionsServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [CloudFunctionsServiceClient, CloudFunctionsServiceAsyncClient]
)
def test_cloud_functions_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "cloudfunctions.googleapis.com:443"


def test_cloud_functions_service_client_get_transport_class():
    transport = CloudFunctionsServiceClient.get_transport_class()
    assert transport == transports.CloudFunctionsServiceGrpcTransport

    transport = CloudFunctionsServiceClient.get_transport_class("grpc")
    assert transport == transports.CloudFunctionsServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            CloudFunctionsServiceClient,
            transports.CloudFunctionsServiceGrpcTransport,
            "grpc",
        ),
        (
            CloudFunctionsServiceAsyncClient,
            transports.CloudFunctionsServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_cloud_functions_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(CloudFunctionsServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(CloudFunctionsServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "never".
    os.environ["GOOGLE_API_USE_MTLS"] = "never"
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class()
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "always".
    os.environ["GOOGLE_API_USE_MTLS"] = "always"
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class()
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_MTLS_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
            client_cert_source=None,
        )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and client_cert_source is provided.
    os.environ["GOOGLE_API_USE_MTLS"] = "auto"
    options = client_options.ClientOptions(
        client_cert_source=client_cert_source_callback
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_MTLS_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
            client_cert_source=client_cert_source_callback,
        )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and default_client_cert_source is provided.
    os.environ["GOOGLE_API_USE_MTLS"] = "auto"
    with mock.patch.object(transport_class, "__init__") as patched:
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=True,
        ):
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=None,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", but client_cert_source and default_client_cert_source are None.
    os.environ["GOOGLE_API_USE_MTLS"] = "auto"
    with mock.patch.object(transport_class, "__init__") as patched:
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=False,
        ):
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                client_cert_source=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS has
    # unsupported value.
    os.environ["GOOGLE_API_USE_MTLS"] = "Unsupported"
    with pytest.raises(MutualTLSChannelError):
        client = client_class()

    del os.environ["GOOGLE_API_USE_MTLS"]


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            CloudFunctionsServiceClient,
            transports.CloudFunctionsServiceGrpcTransport,
            "grpc",
        ),
        (
            CloudFunctionsServiceAsyncClient,
            transports.CloudFunctionsServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_cloud_functions_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            CloudFunctionsServiceClient,
            transports.CloudFunctionsServiceGrpcTransport,
            "grpc",
        ),
        (
            CloudFunctionsServiceAsyncClient,
            transports.CloudFunctionsServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_cloud_functions_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
        )


def test_cloud_functions_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.functions_v1.services.cloud_functions_service.transports.CloudFunctionsServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = CloudFunctionsServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
        )


def test_list_functions(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.ListFunctionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_functions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.ListFunctionsResponse(
            next_page_token="next_page_token_value", unreachable=["unreachable_value"],
        )

        response = client.list_functions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFunctionsPager)

    assert response.next_page_token == "next_page_token_value"

    assert response.unreachable == ["unreachable_value"]


@pytest.mark.asyncio
async def test_list_functions_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.ListFunctionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_functions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.ListFunctionsResponse(
                next_page_token="next_page_token_value",
                unreachable=["unreachable_value"],
            )
        )

        response = await client.list_functions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFunctionsAsyncPager)

    assert response.next_page_token == "next_page_token_value"

    assert response.unreachable == ["unreachable_value"]


def test_list_functions_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.ListFunctionsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_functions), "__call__") as call:
        call.return_value = functions.ListFunctionsResponse()

        client.list_functions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_functions_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.ListFunctionsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_functions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.ListFunctionsResponse()
        )

        await client.list_functions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_functions_pager():
    client = CloudFunctionsServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_functions), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            functions.ListFunctionsResponse(
                functions=[
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                ],
                next_page_token="abc",
            ),
            functions.ListFunctionsResponse(functions=[], next_page_token="def",),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(),], next_page_token="ghi",
            ),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(), functions.CloudFunction(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_functions(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, functions.CloudFunction) for i in results)


def test_list_functions_pages():
    client = CloudFunctionsServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_functions), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            functions.ListFunctionsResponse(
                functions=[
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                ],
                next_page_token="abc",
            ),
            functions.ListFunctionsResponse(functions=[], next_page_token="def",),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(),], next_page_token="ghi",
            ),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(), functions.CloudFunction(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_functions(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_functions_async_pager():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_functions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            functions.ListFunctionsResponse(
                functions=[
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                ],
                next_page_token="abc",
            ),
            functions.ListFunctionsResponse(functions=[], next_page_token="def",),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(),], next_page_token="ghi",
            ),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(), functions.CloudFunction(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_functions(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, functions.CloudFunction) for i in responses)


@pytest.mark.asyncio
async def test_list_functions_async_pages():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_functions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            functions.ListFunctionsResponse(
                functions=[
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                    functions.CloudFunction(),
                ],
                next_page_token="abc",
            ),
            functions.ListFunctionsResponse(functions=[], next_page_token="def",),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(),], next_page_token="ghi",
            ),
            functions.ListFunctionsResponse(
                functions=[functions.CloudFunction(), functions.CloudFunction(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_functions(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_get_function(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.GetFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.CloudFunction(
            name="name_value",
            description="description_value",
            source_archive_url="source_archive_url_value",
            source_upload_url="source_upload_url_value",
            status=functions.CloudFunctionStatus.ACTIVE,
            entry_point="entry_point_value",
            runtime="runtime_value",
            available_memory_mb=1991,
            service_account_email="service_account_email_value",
            version_id=1074,
            network="network_value",
            max_instances=1389,
            vpc_connector="vpc_connector_value",
            vpc_connector_egress_settings=functions.CloudFunction.VpcConnectorEgressSettings.PRIVATE_RANGES_ONLY,
            ingress_settings=functions.CloudFunction.IngressSettings.ALLOW_ALL,
            build_id="build_id_value",
        )

        response = client.get_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.CloudFunction)

    assert response.name == "name_value"

    assert response.description == "description_value"

    assert response.source_archive_url == "source_archive_url_value"

    assert response.source_upload_url == "source_upload_url_value"

    assert response.status == functions.CloudFunctionStatus.ACTIVE

    assert response.entry_point == "entry_point_value"

    assert response.runtime == "runtime_value"

    assert response.available_memory_mb == 1991

    assert response.service_account_email == "service_account_email_value"

    assert response.version_id == 1074

    assert response.network == "network_value"

    assert response.max_instances == 1389

    assert response.vpc_connector == "vpc_connector_value"

    assert (
        response.vpc_connector_egress_settings
        == functions.CloudFunction.VpcConnectorEgressSettings.PRIVATE_RANGES_ONLY
    )

    assert (
        response.ingress_settings == functions.CloudFunction.IngressSettings.ALLOW_ALL
    )

    assert response.build_id == "build_id_value"


@pytest.mark.asyncio
async def test_get_function_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.GetFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.CloudFunction(
                name="name_value",
                description="description_value",
                source_archive_url="source_archive_url_value",
                source_upload_url="source_upload_url_value",
                status=functions.CloudFunctionStatus.ACTIVE,
                entry_point="entry_point_value",
                runtime="runtime_value",
                available_memory_mb=1991,
                service_account_email="service_account_email_value",
                version_id=1074,
                network="network_value",
                max_instances=1389,
                vpc_connector="vpc_connector_value",
                vpc_connector_egress_settings=functions.CloudFunction.VpcConnectorEgressSettings.PRIVATE_RANGES_ONLY,
                ingress_settings=functions.CloudFunction.IngressSettings.ALLOW_ALL,
                build_id="build_id_value",
            )
        )

        response = await client.get_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.CloudFunction)

    assert response.name == "name_value"

    assert response.description == "description_value"

    assert response.source_archive_url == "source_archive_url_value"

    assert response.source_upload_url == "source_upload_url_value"

    assert response.status == functions.CloudFunctionStatus.ACTIVE

    assert response.entry_point == "entry_point_value"

    assert response.runtime == "runtime_value"

    assert response.available_memory_mb == 1991

    assert response.service_account_email == "service_account_email_value"

    assert response.version_id == 1074

    assert response.network == "network_value"

    assert response.max_instances == 1389

    assert response.vpc_connector == "vpc_connector_value"

    assert (
        response.vpc_connector_egress_settings
        == functions.CloudFunction.VpcConnectorEgressSettings.PRIVATE_RANGES_ONLY
    )

    assert (
        response.ingress_settings == functions.CloudFunction.IngressSettings.ALLOW_ALL
    )

    assert response.build_id == "build_id_value"


def test_get_function_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.GetFunctionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_function), "__call__") as call:
        call.return_value = functions.CloudFunction()

        client.get_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_function_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.GetFunctionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_function), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.CloudFunction()
        )

        await client.get_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_function_flattened():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.CloudFunction()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_function(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_function_flattened_error():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_function(
            functions.GetFunctionRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_function_flattened_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.CloudFunction()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.CloudFunction()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_function(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_function_flattened_error_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_function(
            functions.GetFunctionRequest(), name="name_value",
        )


def test_create_function(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.CreateFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.create_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_function_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.CreateFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.create_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_function_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.CreateFunctionRequest()
    request.location = "location/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_function), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.create_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "location=location/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_function_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.CreateFunctionRequest()
    request.location = "location/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_function), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.create_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "location=location/value",) in kw["metadata"]


def test_create_function_flattened():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_function(
            location="location_value",
            function=functions.CloudFunction(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].location == "location_value"
        assert args[0].function == functions.CloudFunction(name="name_value")


def test_create_function_flattened_error():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_function(
            functions.CreateFunctionRequest(),
            location="location_value",
            function=functions.CloudFunction(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_function_flattened_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_function(
            location="location_value",
            function=functions.CloudFunction(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].location == "location_value"
        assert args[0].function == functions.CloudFunction(name="name_value")


@pytest.mark.asyncio
async def test_create_function_flattened_error_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_function(
            functions.CreateFunctionRequest(),
            location="location_value",
            function=functions.CloudFunction(name="name_value"),
        )


def test_update_function(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.UpdateFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.update_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_function_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.UpdateFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.update_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_function_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.UpdateFunctionRequest()
    request.function.name = "function.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_function), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.update_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "function.name=function.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_function_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.UpdateFunctionRequest()
    request.function.name = "function.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_function), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.update_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "function.name=function.name/value",) in kw[
        "metadata"
    ]


def test_update_function_flattened():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_function(function=functions.CloudFunction(name="name_value"),)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].function == functions.CloudFunction(name="name_value")


def test_update_function_flattened_error():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_function(
            functions.UpdateFunctionRequest(),
            function=functions.CloudFunction(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_function_flattened_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_function(
            function=functions.CloudFunction(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].function == functions.CloudFunction(name="name_value")


@pytest.mark.asyncio
async def test_update_function_flattened_error_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_function(
            functions.UpdateFunctionRequest(),
            function=functions.CloudFunction(name="name_value"),
        )


def test_delete_function(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.DeleteFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_function_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.DeleteFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.delete_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_function_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.DeleteFunctionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_function), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.delete_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_function_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.DeleteFunctionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_function), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.delete_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_function_flattened():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_function(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_function_flattened_error():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_function(
            functions.DeleteFunctionRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_function_flattened_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_function(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_function_flattened_error_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_function(
            functions.DeleteFunctionRequest(), name="name_value",
        )


def test_call_function(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.CallFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.call_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.CallFunctionResponse(
            execution_id="execution_id_value",
            result="result_value",
            error="error_value",
        )

        response = client.call_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.CallFunctionResponse)

    assert response.execution_id == "execution_id_value"

    assert response.result == "result_value"

    assert response.error == "error_value"


@pytest.mark.asyncio
async def test_call_function_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.CallFunctionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.call_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.CallFunctionResponse(
                execution_id="execution_id_value",
                result="result_value",
                error="error_value",
            )
        )

        response = await client.call_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.CallFunctionResponse)

    assert response.execution_id == "execution_id_value"

    assert response.result == "result_value"

    assert response.error == "error_value"


def test_call_function_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.CallFunctionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.call_function), "__call__") as call:
        call.return_value = functions.CallFunctionResponse()

        client.call_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_call_function_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.CallFunctionRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.call_function), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.CallFunctionResponse()
        )

        await client.call_function(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_call_function_flattened():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.call_function), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.CallFunctionResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.call_function(
            name="name_value", data="data_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"
        assert args[0].data == "data_value"


def test_call_function_flattened_error():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.call_function(
            functions.CallFunctionRequest(), name="name_value", data="data_value",
        )


@pytest.mark.asyncio
async def test_call_function_flattened_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.call_function), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.CallFunctionResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.CallFunctionResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.call_function(name="name_value", data="data_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"
        assert args[0].data == "data_value"


@pytest.mark.asyncio
async def test_call_function_flattened_error_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.call_function(
            functions.CallFunctionRequest(), name="name_value", data="data_value",
        )


def test_generate_upload_url(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.GenerateUploadUrlRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.generate_upload_url), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.GenerateUploadUrlResponse(
            upload_url="upload_url_value",
        )

        response = client.generate_upload_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.GenerateUploadUrlResponse)

    assert response.upload_url == "upload_url_value"


@pytest.mark.asyncio
async def test_generate_upload_url_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.GenerateUploadUrlRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.generate_upload_url), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.GenerateUploadUrlResponse(upload_url="upload_url_value",)
        )

        response = await client.generate_upload_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.GenerateUploadUrlResponse)

    assert response.upload_url == "upload_url_value"


def test_generate_upload_url_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.GenerateUploadUrlRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.generate_upload_url), "__call__"
    ) as call:
        call.return_value = functions.GenerateUploadUrlResponse()

        client.generate_upload_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_generate_upload_url_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.GenerateUploadUrlRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.generate_upload_url), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.GenerateUploadUrlResponse()
        )

        await client.generate_upload_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_generate_download_url(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.GenerateDownloadUrlRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.generate_download_url), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = functions.GenerateDownloadUrlResponse(
            download_url="download_url_value",
        )

        response = client.generate_download_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.GenerateDownloadUrlResponse)

    assert response.download_url == "download_url_value"


@pytest.mark.asyncio
async def test_generate_download_url_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = functions.GenerateDownloadUrlRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.generate_download_url), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.GenerateDownloadUrlResponse(download_url="download_url_value",)
        )

        response = await client.generate_download_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, functions.GenerateDownloadUrlResponse)

    assert response.download_url == "download_url_value"


def test_generate_download_url_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.GenerateDownloadUrlRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.generate_download_url), "__call__"
    ) as call:
        call.return_value = functions.GenerateDownloadUrlResponse()

        client.generate_download_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_generate_download_url_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = functions.GenerateDownloadUrlRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.generate_download_url), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            functions.GenerateDownloadUrlResponse()
        )

        await client.generate_download_url(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_set_iam_policy(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy(version=774, etag=b"etag_blob",)

        response = client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_set_iam_policy_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy.Policy(version=774, etag=b"etag_blob",)
        )

        response = await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_set_iam_policy_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        call.return_value = policy.Policy()

        client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_set_iam_policy_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_iam_policy), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())

        await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_set_iam_policy_from_dict():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        response = client.set_iam_policy(
            request={
                "resource": "resource_value",
                "policy": policy.Policy(version=774),
            }
        )
        call.assert_called()


def test_get_iam_policy(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy(version=774, etag=b"etag_blob",)

        response = client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_get_iam_policy_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy.Policy(version=774, etag=b"etag_blob",)
        )

        response = await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_get_iam_policy_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        call.return_value = policy.Policy()

        client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_iam_policy_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_iam_policy), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())

        await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_get_iam_policy_from_dict():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        response = client.get_iam_policy(
            request={
                "resource": "resource_value",
                "options": options.GetPolicyOptions(requested_policy_version=2598),
            }
        )
        call.assert_called()


def test_test_iam_permissions(transport: str = "grpc"):
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.TestIamPermissionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse(
            permissions=["permissions_value"],
        )

        response = client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


@pytest.mark.asyncio
async def test_test_iam_permissions_async(transport: str = "grpc_asyncio"):
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.TestIamPermissionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse(permissions=["permissions_value"],)
        )

        response = await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


def test_test_iam_permissions_field_headers():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = iam_policy.TestIamPermissionsResponse()

        client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_test_iam_permissions_field_headers_async():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse()
        )

        await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_test_iam_permissions_from_dict():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        response = client.test_iam_permissions(
            request={
                "resource": "resource_value",
                "permissions": ["permissions_value"],
            }
        )
        call.assert_called()


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.CloudFunctionsServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = CloudFunctionsServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.CloudFunctionsServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = CloudFunctionsServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.CloudFunctionsServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = CloudFunctionsServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.CloudFunctionsServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = CloudFunctionsServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.CloudFunctionsServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.CloudFunctionsServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    assert isinstance(client._transport, transports.CloudFunctionsServiceGrpcTransport,)


def test_cloud_functions_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.CloudFunctionsServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_cloud_functions_service_base_transport():
    # Instantiate the base transport.
    transport = transports.CloudFunctionsServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "list_functions",
        "get_function",
        "create_function",
        "update_function",
        "delete_function",
        "call_function",
        "generate_upload_url",
        "generate_download_url",
        "set_iam_policy",
        "get_iam_policy",
        "test_iam_permissions",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_cloud_functions_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(auth, "load_credentials_from_file") as load_creds:
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.CloudFunctionsServiceTransport(
            credentials_file="credentials.json",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
        )


def test_cloud_functions_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        CloudFunctionsServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_cloud_functions_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.CloudFunctionsServiceGrpcTransport(host="squid.clam.whelk")
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_cloud_functions_service_host_no_port():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="cloudfunctions.googleapis.com"
        ),
    )
    assert client._transport._host == "cloudfunctions.googleapis.com:443"


def test_cloud_functions_service_host_with_port():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="cloudfunctions.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "cloudfunctions.googleapis.com:8000"


def test_cloud_functions_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.CloudFunctionsServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_cloud_functions_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.CloudFunctionsServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_cloud_functions_service_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.CloudFunctionsServiceGrpcTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=("https://www.googleapis.com/auth/cloud-platform",),
        ssl_credentials=mock_ssl_cred,
    )
    assert transport.grpc_channel == mock_grpc_channel


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_cloud_functions_service_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.CloudFunctionsServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=("https://www.googleapis.com/auth/cloud-platform",),
        ssl_credentials=mock_ssl_cred,
    )
    assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_cloud_functions_service_grpc_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.CloudFunctionsServiceGrpcTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=mock_ssl_cred,
        )
        assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_cloud_functions_service_grpc_asyncio_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.CloudFunctionsServiceGrpcAsyncIOTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=mock_ssl_cred,
        )
        assert transport.grpc_channel == mock_grpc_channel


def test_cloud_functions_service_grpc_lro_client():
    client = CloudFunctionsServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_cloud_functions_service_grpc_lro_async_client():
    client = CloudFunctionsServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client._client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_cloud_function_path():
    project = "squid"
    location = "clam"
    function = "whelk"

    expected = "projects/{project}/locations/{location}/functions/{function}".format(
        project=project, location=location, function=function,
    )
    actual = CloudFunctionsServiceClient.cloud_function_path(
        project, location, function
    )
    assert expected == actual


def test_parse_cloud_function_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "function": "nudibranch",
    }
    path = CloudFunctionsServiceClient.cloud_function_path(**expected)

    # Check that the path construction is reversible.
    actual = CloudFunctionsServiceClient.parse_cloud_function_path(path)
    assert expected == actual