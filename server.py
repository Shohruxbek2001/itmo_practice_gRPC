import grpc
from concurrent import futures
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from google.protobuf.empty_pb2 import Empty

import glossary_pb2
import glossary_pb2_grpc

DATABASE_URL = "sqlite:///./terms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TermModel(Base):
    __tablename__ = "terms"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True)
    definition = Column(String)

Base.metadata.create_all(bind=engine)


initial_terms = [
    {
        "term": "Apache Spark",
        "definition": "Распределенная вычислительная система с открытым исходным кодом для обработки больших данных"
    },
    {
        "term": "Hadoop",
        "definition": "Фреймворк для распределенного хранения и обработки больших данных на кластерах"
    },
    {
        "term": "Scala",
        "definition": "Язык программирования, используемый для разработки приложений на Apache Spark"
    },
    {
        "term": "Hue",
        "definition": "Веб-интерфейс для взаимодействия с Hadoop и анализа данных"
    },
    {
        "term": "Jenkins",
        "definition": "Инструмент для автоматизации процессов CI/CD (непрерывной интеграции и доставки)"
    },
    {
        "term": "Jupyter",
        "definition": "Интерактивная платформа для работы с данными и выполнения аналитических запросов"
    },
    {
        "term": "MobXterm",
        "definition": "Инструмент для работы с удаленными серверами и выполнения команд"
    },
    {
        "term": "Data Mining",
        "definition": "Процесс обнаружения закономерностей в больших наборах данных"
    },
    {
        "term": "SQL",
        "definition": "Язык структурированных запросов для работы с реляционными базами данных"
    },
    {
        "term": "Unit-тесты",
        "definition": "Тестирование отдельных модулей или компонентов системы"
    },
    {
        "term": "PuTTY",
        "definition": "Клиент для подключения к серверам по протоколам SSH и Telnet"
    },
    {
        "term": "Инкрементальный расчет",
        "definition": "Метод обработки данных, при котором пересчитываются только измененные записи"
    },
    {
        "term": "Change Data Capture (CDC)",
        "definition": "Технология отслеживания изменений в данных"
    }
]


def init_db():
    db = SessionLocal()
    for term in initial_terms:
        if not db.query(TermModel).filter(TermModel.term == term["term"]).first():
            db.add(TermModel(**term))
    db.commit()
    db.close()


class DictionaryService(glossary_pb2_grpc.DictionaryServiceServicer):
    def GetAllTerms(self, request, context):
        db = SessionLocal()
        terms = db.query(TermModel).all()
        db.close()
        return glossary_pb2.TermsList(
            terms=[glossary_pb2.Term(id=t.id, term=t.term, definition=t.definition) for t in terms]
        )

    def GetTerm(self, request, context):
        db = SessionLocal()
        term = db.query(TermModel).filter(TermModel.term == request.term).first()
        db.close()
        if term:
            return glossary_pb2.GetTermResponse(
                term=glossary_pb2.Term(id=term.id, term=term.term, definition=term.definition)
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Term not found")
        return glossary_pb2.GetTermResponse()

    def AddTerm(self, request, context):
        db = SessionLocal()
        new_term = TermModel(
            term=request.term.term,
            definition=request.term.definition,
        )
        db.add(new_term)
        db.commit()
        db.close()
        return glossary_pb2.AddTermResponse(message="Term added successfully!")

    def UpdateTerm(self, request, context):
        db = SessionLocal()
        term = db.query(TermModel).filter(TermModel.id == request.term.id).first()
        if term:
            term.term = request.term.term
            term.definition = request.term.definition
            db.commit()
            db.close()
            return glossary_pb2.UpdateTermResponse(message="Term updated successfully!")
        db.close()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Term not found")
        return glossary_pb2.UpdateTermResponse(message="Term not found")

    def DeleteTerm(self, request, context):
        db = SessionLocal()
        term = db.query(TermModel).filter(TermModel.id == request.id).first()  # Удаляем по ID
        if term:
            db.delete(term)
            db.commit()
            db.close()
            return glossary_pb2.DeleteTermResponse(message="Term deleted successfully!")
        db.close()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Term not found")
        return glossary_pb2.DeleteTermResponse(message="Term not found")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_DictionaryServiceServicer_to_server(DictionaryService(), server)
    server.add_insecure_port("[::]:50051")
    print("gRPC server is running on port 50051")
    init_db()
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()