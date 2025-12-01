from setuptools import setup

setup(
    name="shared",
    version="0.1.0",
    description="Shared CQRS and Infrastructure Components",
    packages=["shared"],
    package_dir={"shared": "."},
    py_modules=[
        "auth",
        "cqrs_base",
        "database",
        "event_bus",
        "monitoring",
    ],
    install_requires=[
        "flask==3.0.0",
        "flask-cors==4.0.0",
        "psycopg2-binary==2.9.9",
        "sqlalchemy==2.0.23",
        "pika==1.3.2",
        "prometheus-client==0.19.0",
        "pyjwt==2.8.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.11",
)
