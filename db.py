from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://NR33tiuABb2cnMd.root:OCAuMbNZOaTuT74o@gateway01.ap-northeast-1.prod.aws.tidbcloud.com:4000/test?ssl_ca=/etc/ssl/certs/ca-certificates.crt"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl":{
            "ssl":True
        }
    }
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()