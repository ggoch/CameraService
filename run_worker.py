import argparse
import os
from dotenv import load_dotenv
from celery import Celery

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    parser.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    parser.add_argument("--test",action="store_true", help="Run the server in test mode.")
    parser.add_argument("--dev",action="store_true", help="Run the server in development mode.")
    
    db_type =  parser.add_argument_group(title="Database Type", description="Run the server in different database type.")
    db_type.add_argument("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")

    # run_mode = parser.add_argument_group(title="Run Mode", description="Run the server in Async or Sync mode. Default is Async.")
    # run_mode.add_argument("--sync",action="store_true", help="Run the server in Sync mode.")

    args = parser.parse_args()

    if args.prod:
        load_dotenv("setting/.env.prod")
    elif args.test:
        load_dotenv("setting/.env.test")
    else:
        load_dotenv("setting/.env.dev")

    os.environ["RUN_MODE"] = "SYNC"

    os.environ["DB_TYPE"] = args.db

     # 運行 Celery 工作進程的命令
    os.system('celery -A works.celery_main worker --loglevel=info -P eventlet')
    # os.system('celery -A works.celery_main worker --loglevel=info')