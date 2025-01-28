# ✉️ Failmail

`Failmail`  is a Python package designed to send email notifications when exceptions are raised in your application.
It offers an easy-to-use registry system to associate specific exceptions with customizable email alerts.
You can specify the recipients, subject, body, and format (plain-text or HTML) for the notifications. 

**Note: ``Failmail`` is in early development. The API may change as new features are added and refined.**


## 🌱 Getting Started

### 🔧 Installation

To install the package, run:

```bash
pip install failmail
```

For the latest development version directly from the repository, use:

```bash
pip install git+https://github.com/spyel/failmail.git
```

### 🖥️ Usage

First, create an instance of ``ExceptionNotifier`` and configure it with your SMTP server details:

```python
from failmail import ExceptionNotifier

# Set up the notifier with your SMTP server details
notifier = ExceptionNotifier(
    host=('smtp.example.com', 587),       # SMTP server address and port
    sender_email='sender@example.com',    # Sender's email address
    credentials=('username', 'password'), # SMTP login credentials (optional)
    encryption='tls'                      # Encryption type: 'tls' or 'ssl' or 'none'
)
```

Next, register specific exceptions along with their corresponding email notifications.
You can define the recipients, subject, body, and the format of the email (either ``plain`` or ``html``):

```python
notifier.register_exception(
    exception_type=ValueError,  # The exception to register
    recipients=['admin@example.com'],
    subject='Error: ${error_type} occurred',
    body='An error of type ${error_type} occurred at ${timestamp}.\n\nMessage: ${error_message}\n\nTraceback:\n${error_traceback}',
    body_type='plain'  # Use 'html' for HTML format
)
````

When an exception occurs, use the ``notify()`` method to send the email notification:

```python
try:
    # Some code that may raise an exception
    raise ValueError("Something went wrong!")
except Exception as e:
    # Notify recipients when an exception is raised
    notifier.notify(e)
````

You can also include additional context to customize the email notification.
This context will be used to format the subject and body of the email:

```python
additional_context = {
    'custom_info': 'Additional data for the notification'
}
notifier.notify(e, additional_context=additional_context)
```


## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
