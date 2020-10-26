# Hopper 

Based on the [emailtrail](https://github.com/akshaykmr/emailtrail/pull/3/files) project, hopper is a python 2 & 3 package to track received from header hops.

Get structured information about each hop - Hostnames, Protocol used, Timestamp, and Delay.

## Table of Contents

- [Usage](#usage)
- [Caveats](#caveats)
- [Contributing](#contributing)
- [Miscellaneous](#miscellaneous)

## Usage

We can analyse an email source or raw headers

```python
email = """
Delivered-To: money@capitalism.com
Received: by 10.129.52.209 with SMTP id b200csp1430876ywa;
        Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
X-Received: by 10.31.153.20 with SMTP id b20mr6116862vke.110.1507623422746;
        Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
Received: from mail-sor-f65.google.com (mail-sor-f65.google.com. [209.85.220.65])
        by mx.google.com with SMTPS id b31sor1345013uaa.124.2017.10.10.01.17.02
        for <money@capitalism.com>
        (Google Transport Security);
        Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
Received-SPF: pass (google.com: domain of bags@test_email.ua.edu designates 209.85.220.65 as permitted sender) client-ip=209.85.220.65;
X-Received: by 10.176.85.196 with SMTP id w4mr6874179uaa.75.1507623422198; Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
MIME-Version: 1.0
Received: by 10.103.79.86 with HTTP; Tue, 10 Oct 2017 01:17:01 -0700 (PDT)
From: Mr. Money Bags <bags@moneyrules.com>
Date: Tue, 10 Oct 2017 01:17:01 -0700
Subject:
To: money@capitalism.com;
Content-Type: text/plain; charset="UTF-8"
Bcc: satan@wallstreet.com

A business opportunity awaits
"""
```

#### Lets analyse it

```python
from hopper import Hopper
Hopper.analyse(email)
```

```python
{
  'To': u'money@capitalism.com;',
  'From': u'Mr. Money Bags <bags@moneyrules.com>',
  'Bcc': u'satan@wallstreet.com',
  'Cc': u'None',
  'total_delay': 1,
  'trail': [
    {
      'delay': 0,
      'from': '',
      'protocol': 'HTTP',
      'receivedBy': '10.103.79.86',
      'timestamp': 1507623421
    },
    {
      'delay': 1,
      'from': 'mail-sor-f65.google.com',
      'protocol': 'SMTPS',
      'receivedBy': 'mx.google.com',
      'timestamp': 1507623422
    },
    {
      'delay': 0,
      'from': '',
      'protocol': 'SMTP',
      'receivedBy': '10.129.52.209',
      'timestamp': 1507623422
    }
  ]
}

```
The analyse function returns a python dictionary.

The trail shows the email hops sorted in chronological order. Each intermediary email server adds a `Received` header to the mail, from which the module parses the following information:

- `protocol`  : e.g HTTP, SMTP etc.
- `from`      : The name the sending computer gave for itself
- `receivedBy`: The receiving computers name
- `timestamp` : Unix epoch

An empty string value is set for fields which couldn't be determined.

- `delay`: The delay (in seconds) is computed by taking the difference of two consecutive hops. In above example there was a delay of `1 sec ` from `10.103.79.86` to `mx.google.com`

### Caveats

Sometimes during delay calculation the timestamp difference may be negative. 
  - It's not possible for a server to recieve the email before previous one,
  - It means that either one or both of the servers clocks are off.
  - We assume a delay of `0` for this hop.

## Contributing

emailtrail uses [pipenv](http://pipenv.org/) for managing virtual env and package versions.

- Fork the repo and clone it.
- In project root: `pipenv install --dev --two`. This installs packages required for testing and linting
- Jump into your virutal env: `pipenv shell`
- Running tests: `pytest`
- If you want to understand the code, read the test cases first.
- Make your changes -> Pass the tests -> Push to your branch -> Create pull request -> Profit ??
