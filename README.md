# 1. Project Overview

The Corporate Action Workflow System is a backend application designed to model, validate, queue, and process corporate actions such as dividends, splits, and mergers. It demonstrates a clean, scalable architecture built around workflow‑driven processing, persistent state management, and a dual‑interface design (CLI + REST API).

This project was created to showcase my approach to backend application engineering: clear separation of concerns, strong domain modeling, workflow/state‑machine design, persistent queues, pluggable processing strategies, and test‑driven development. The system is intentionally structured to reflect production‑grade engineering practices rather than one‑off scripts or tightly coupled logic.

At a high level, the application provides:

- A **domain model** representing corporate actions and their lifecycle  
- A **persistent queue** that stores actions and tracks their state  
- A **processing engine** that validates and executes workflow transitions  
- A **CLI interface** for local interaction and automation  
- A **REST API** for programmatic access and integration  
- A **test suite** validating correctness, behavior, and edge cases  

The result is a compact but realistic example of how to build a workflow‑oriented backend system that is modular, extensible, and easy to maintain.

# 2. Key Architectural Principles

This architecture emphasizes clarity, modularity, and long‑term maintainability, demonstrating how workflow‑driven systems can be built in a clean and extensible way.

## Separation of Concerns
Data driven domain modeling, persistence, workflow processing, API routing, and CLI interaction are isolated into their own modules. This keeps the system easy to reason about and prevents cross‑layer coupling.

## Domain‑Driven Modeling
Corporate actions are represented as first‑class domain objects with explicit state, validation rules, and lifecycle transitions. The `CorporateAction` model and `CorporateActionStatus` enum form the core of the system’s domain layer.

## Workflow / State‑Machine Design
Corporate actions move through a well‑defined sequence of states: `RECEIVED → VALIDATED → PROCESSING → COMPLETED` (or `FAILED`). This explicit state machine makes the workflow predictable, testable, and easy to extend.

## Persistence Abstraction
The system uses a JSON‑backed persistent queue to store actions. The persistence layer is abstracted behind a simple interface, making it easy to replace with a database, message queue, or cloud storage without changing business logic.

## Pluggable Processing Strategies
The processing engine is designed to support multiple strategies for different action types. This allows new corporate action categories or business rules to be added without modifying existing logic.

## Dual Interface: CLI and REST API
The application exposes both:
- A **CLI** for local workflows, automation, and developer interaction  
- A **REST API** for integration with external systems  

Both interfaces operate on the same queue and processor, demonstrating how to build multiple front‑ends on a shared backend core.

## Test‑Driven Development
The project includes a comprehensive test suite covering:
- Domain validation  
- Queue and persistence behavior  
- Processing strategies and logic
- API endpoints  

This ensures correctness and provides confidence when extending or refactoring the system.

### Note on CLI Testing

The CLI layer is intentionally not included in the automated test suite. It serves as a thin wrapper around the underlying queue and processor, both of which are fully tested. While subprocess‑based CLI testing is possible, it adds unnecessary complexity and overhead without improving confidence in the system’s behavior.

## Extensibility and Scalability
The architecture is intentionally modular:
- New action types can be added easily  
- Processing rules can evolve independently  
- The persistence layer can be swapped out  
- Logging, metrics, and observability can be layered on without disruption  

This reflects how real‑world backend systems grow over time.

# 3. System Architecture

The Corporate Action Workflow System is built around a set of modular components that work together to model, store, validate, and process corporate actions. Each layer has a clearly defined responsibility.

## 3.1 Architectural Overview

The system is composed of five primary layers:

1. **Domain Model** – Defines corporate actions, their attributes, and lifecycle states.  
2. **Persistent Queue** – Stores actions durably and exposes queue operations.  
3. **Processing Engine** – Validates and advances actions through workflow states.  
4. **CLI Interface** – Provides a command‑line front‑end for interacting with the system.  
5. **REST API** – Exposes the workflow engine over HTTP for integration and automation.

These layers are intentionally decoupled so that each can evolve independently.

## 3.2 Domain Model

The domain layer defines the core business concepts:

- `CorporateAction` – A dataclass representing a single corporate action.  
- `CorporateActionStatus` – An enum defining the workflow states:  
  `RECEIVED → VALIDATED → PROCESSING → COMPLETED` (or `FAILED`).

The model includes:

- Validation rules  
- State‑transition helpers  
- Serialization/deserialization (`to_dict`, `from_dict`)  

This ensures that business rules live *with* the domain objects, not scattered across the system.

## 3.3 Persistent Queue

The queue layer provides durable storage and retrieval of actions.

### Components:
- `JsonStore` – Handles low‑level JSON file I/O.  
- `PersistentQueue` – Wraps the store and exposes queue operations:
  - `enqueue`
  - `dequeue`
  - `update`
  - `all`
  - `peek`
  - `size`
  - `is_empty`

Actions are always loaded as full `CorporateAction` objects, ensuring consistent types across the system.

This abstraction allows the JSON store to be replaced with a database or message queue without changing business logic.

## 3.4 Processing Engine

The `ActionProcessor` is responsible for:

- Calling validating actions  
- Transitioning them through workflow states    
- Updating the persistent queue  

The processor is intentionally simple but structured to support pluggable strategies for different action types.

### Note on Logging

A placeholder logging hook is included in the processor to show where workflow events would be captured in a production system. Full logging was intentionally deferred for a later iteration to keep the initial version focused on core architecture, workflow design, and test coverage. This ensures the project remains lightweight while still demonstrating awareness of where observability concerns fit into the system.

## 3.5 CLI Interface

The CLI provides a local, scriptable interface for interacting with the system. It supports:

- Creating actions  
- Listing actions  
- Processing the next action  
- Viewing stats  
- Clearing the queue  

The CLI and API share the same underlying queue and processor, demonstrating how multiple interfaces can operate on a shared backend core.

## 3.6 REST API (FastAPI)

The API exposes the workflow engine over HTTP. Endpoints include:

- `POST /actions` – Create a new action  
- `POST /actions/process` – Process the next action  
- `GET /actions` – List all actions  
- `GET /actions/{id}` – Inspect a specific action  
- `GET /stats` – Retrieve action counts by status  
- `DELETE /actions` – Clear all actions  

The API layer is intentionally thin, delegating all business logic to the queue and processor.

## 3.7 Design Goals

The architecture is intentionally structured to demonstrate:

- Clean layering  
- Strong domain modeling  
- Workflow‑driven design  
- Persistence abstraction  
- Extensibility  
- Testability  
- Real‑world engineering patterns  

This system is small by design, but it reflects the same principles used in production‑grade backend applications.

# 4. Installation & Setup

This project is structured as a Python package and is intended to be installed in editable mode during development. The steps below outline how to set up a clean environment, install dependencies, and run both the CLI and API interfaces.

## 4.1 Requirements

- **Python 3.11+**
- **pip** (latest recommended)
- **virtualenv** or **venv** for environment isolation

The project has no external service dependencies; all persistence is handled locally via a JSON store.

## 4.2 Create and Activate a Virtual Environment

It is strongly recommended to use a dedicated virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
```

## 4.3 Install the Project in Editable Mode

Editable installation ensures that changes to the source code are immediately reflected without reinstalling the package.

From the project root:

```bash
pip install -e .
```

This installs:

- The corporate_action_workflow_app package
- All required dependencies
- The CLI entry point

## 4.4 Verify Installation

You can confirm the installation by running:

```bash
first-app --help
```

This will display the available CLI commands, while also confirming the install.

## 4.5 Running the CLI

Once installed, the CLI is available globally:

```bash
first-app create --type DIVIDEND --amount 4.22
first-app list
first-app process
first-app stats
first-app clear
```

The CLI interacts with the same persistent queue and processor used by the API

## 4.6 Running the API Server

The API is built with FastAPI and can be launched using Uvicorn:

Once running, the API is available at:

 - http://localhost:8000

Interactive documentation is automatically generated at:

 - Swagger UI: http://localhost:8000/docs
 - ReDoc: http://localhost:8000/redoc

 ## 4.7 Project Structure

 A simplified view of the repository layout:

src/
  corporate_action_workflow_app/
      api/
      cli/
      models/
      persistence/
      processor/
      queue/
      services/
tests/
pyproject.toml
README.md
requirements.txt

# 5. Extending the System

The Corporate Action Workflow System is intentionally designed to be modular and extensible. Each major component — domain model, queue, processor, CLI, and API—can evolve independently without requiring large‑scale refactoring. This section outlines the primary extension points and how the system can grow to support more complex workflows or production‑grade requirements.

## 5.1 Adding New Corporate Action Types

New action types can be introduced by extending the domain model:

- Add a new `CorporateActionType` 
- Define any additional metadata fields required for the new action.
- Implement validation rules within the model.
- Add processing logic in the `ActionProcessor` or a dedicated strategy class.

Because the system uses a shared serialization format (`to_dict` / `from_dict`), new fields are automatically persisted without changes to the storage layer.

## 5.2 Adding New Processing Strategies

The processing engine is structured to support multiple strategies based on action type. To introduce a new strategy:

- Create a new handler or method that encapsulates the business logic.
- Register or route the new strategy inside the processor.
- Update tests to cover the new workflow path.

This approach keeps the processor clean and prevents action‑specific logic from becoming tangled.

## 5.3 Replacing the Persistence Layer

The current implementation uses a JSON‑backed store for simplicity. It can be replaced with:

- SQLite or PostgreSQL  
- Redis or another in‑memory store  
- A message queue (RabbitMQ, SQS, Kafka)  
- Cloud storage (S3, Azure Blob, GCS)

Because persistence is abstracted behind `JsonStore` and `PersistentQueue`, replacing the storage mechanism requires only implementing the same interface.

## 5.4 Extending the CLI

The CLI is built on top of the same queue and processor used by the API. New commands can be added by:

- Creating a new subcommand in the CLI module.
- Calling into the queue or processor as needed.
- Adding help text and usage examples.

This allows the CLI to grow alongside the system without duplicating logic.

## 5.5 Extending the API

The FastAPI layer is intentionally thin. To add new endpoints:

- Implement a new route function.
- Delegate business logic.
- Return serialized `CorporateAction` objects or custom responses.

Because the API does not contain business logic, it remains easy to maintain and expand.

## 5.6 Adding Logging, Metrics, or Observability

The system is ready for production‑style instrumentation:

- Logging middleware or a dedicated logging service  
- Structured logs for each workflow transition  
- Metrics for queue depth, processing time, and error rates  
- Tracing for end‑to‑end workflow visibility  

These can be added without modifying core business logic.

## 5.7 Scaling the Architecture

The system can scale in several directions:

- Multiple processors running concurrently  
- Distributed queues or message brokers  
- Horizontal scaling of API instances  
- Background workers for asynchronous processing  
- Event‑driven architectures for real‑time workflows  

The clean separation of concerns makes these evolutions straightforward.

## 5.8 Summary

The system is intentionally small but architecturally robust. Its modular design allows it to grow into a more complex workflow engine without sacrificing clarity or maintainability. Each layer can be extended independently, making the project a strong foundation for demonstrating real‑world backend engineering practices.

# 6. Roadmap

The following roadmap outlines planned enhancements that build on the existing foundation and demonstrate how the system can evolve into a more production‑ready workflow engine.

## 6.1 Logging and Observability

Introduce a structured logging layer that captures:

- Workflow state transitions  
- Validation outcomes  
- Processing durations  
- Errors and exceptions  
- Queue depth and throughput  

This may include a dedicated logging service, log sinks, or integration with tools like ELK, OpenTelemetry, or cloud‑native logging platforms.

## 6.2 Metrics and Monitoring

Add instrumentation to expose operational metrics such as:

- Number of actions processed  
- Processing latency  
- Failure rates  
- Queue size over time  

These metrics can be exported to Prometheus, Grafana, or similar systems to support monitoring and alerting.

## 6.3 Enhanced Persistence Options

Replace or augment the JSON store with more scalable backends:

- SQLite or PostgreSQL  
- Redis for in‑memory queueing  
- Cloud storage (S3, Azure Blob, GCS)  
- Message queues (RabbitMQ, SQS, Kafka)

The existing persistence abstraction makes this transition straightforward.

## 6.4 Expanded Domain Modeling

Add support for more complex corporate action types:

- Rights offerings  
- Spin‑offs  
- Tender offers  
- Reorganizations  

Each new type can include its own validation rules and processing strategies.

## 6.5 Administrative and Developer Tooling

Potential additions include:

- Developer utilities for replaying or simulating workflows  
- CLI enhancements for batch operations  
- API keys or authentication for secured environments  

## 6.7 Deployment and Packaging

Prepare the system for deployment:

- Docker containerization  
- CI/CD pipeline  
- Environment‑based configuration  
- Production‑grade server setup  

These steps help demonstrate operational readiness.

## 6.8 Lightweight UI and Deployment Example

A lightweight UI can be added to provide a simple dashboard for viewing corporate actions, triggering processing, and inspecting system state. This could be implemented using a small frontend framework (e.g., Svelte, Vue, or React) and would communicate with the existing FastAPI backend via JSON.

To demonstrate deployment readiness, the system can be packaged into containers and deployed to a small production‑like environment such as Fly.io, Railway, or a Docker Compose setup. This would include:

- Containerizing the API and UI  
- Adding environment‑based configuration  
- Providing a sample deployment configuration (e.g., `docker-compose.yml`)  
- Optionally introducing CORS settings and basic build automation  

This enhancement highlights the system’s ability to support a UI layer and operate in a realistic deployment environment without expanding the project beyond its intended scope.

## 6.9 Long‑Term Vision

The long‑term goal is to evolve this project into a fully featured workflow engine capable of:

- Handling diverse corporate action types  
- Scaling horizontally  
- Integrating with external systems  
- Providing observability and operational insights  
- Supporting real‑world financial processing workloads  

The current architecture is intentionally designed to support this growth.
