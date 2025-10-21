# Distributed Cab Booking System (CabConnect)

A full-fledged cab booking system designed with distributed systems principles. This application features a responsive React/Tailwind frontend, Python RPC backend with load balancing, clock synchronization, and data consistency.

## System Architecture

This system follows a distributed architecture with the following components:

- **Frontend**: React + Vite + Tailwind CSS for a responsive, modern UI
- **Backend**: Python-based RPC services with load balancing
- **API Gateway**: RESTful API interface for the frontend
- **Clock Synchronization**: NTP-based time synchronization with Lamport logical clocks
- **Data Consistency**: Vector clocks and synchronous/asynchronous replication

## Key Features

- **Load Balancing**: Least-connections algorithm to distribute client requests
- **Fault Tolerance**: Multiple server instances with automatic failover
- **Clock Synchronization**: NTP with Lamport logical clocks for event ordering
- **Data Consistency**: Vector clocks to track causality and resolve conflicts
- **Distributed Consensus**: Leader-based replication for data consistency

## User Features

- **User Registration & Authentication**: For both riders and drivers
- **Ride Booking**: Book cabs with fare estimation
- **Real-time Ride Tracking**: Track ride status updates
- **Driver Availability**: Drivers can set their availability and location
- **Ride Management**: Accept, start, complete, or cancel rides
- **Rating System**: Rate drivers and riders after rides

## Project Structure

```
backend/
  ├── config/              # Configuration settings
  ├── models/              # Data models (User, Ride)
  ├── services/            # Core business logic
  │   ├── api_gateway.py   # RESTful API interface
  │   ├── cab_service.py   # Main service implementation
  │   └── load_balancer.py # Request distribution
  └── util/                # Utility functions
      └── clock/           # Clock synchronization implementations

frontend/
  ├── public/              # Static assets
  ├── src/
  │   ├── components/      # Reusable UI components
  │   ├── context/         # React Context API providers
  │   ├── pages/           # Application pages
  │   └── services/        # API services
  ├── index.html           # HTML entry point
  └── vite.config.js       # Vite configuration
```

## Installation and Setup

### Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cabconnect.git
   cd cabconnect
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API Gateway:
   ```bash
   cd backend
   python services/api_gateway.py
   ```

4. Start multiple cab service instances (in separate terminals):
   ```bash
   python services/cab_service.py --port 9000 --id 1
   python services/cab_service.py --port 9001 --id 2
   python services/cab_service.py --port 9002 --id 3
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Access the application at `http://localhost:5173`

## Running Alternative RPC/RMI Implementations

### Python XML-RPC
```bash
# Start server
cd RPC
python cab_server.py

# Start client
python cab_client.py
```

### Java RMI
```bash
# Compile Java files
cd RMI
javac *.java

# Start RMI registry
rmiregistry &

# Start server
java CabServer

# Start client
java CabClient
```

### WebSocket Implementation
```bash
# Start server
cd WebSocket
python cab_server.py

# Start client
python cab_client.py
```

## References & Concepts

This implementation is inspired by the concepts explained in:
- [Remote Procedure Call (RPC)](https://www.geeksforgeeks.org/operating-systems/remote-procedure-call-rpc-in-operating-system/)
- [Java Remote Method Invocation (RMI)](https://www.geeksforgeeks.org/java/remote-method-invocation-in-java/)
- [Berkeley's Algorithm](https://www.geeksforgeeks.org/operating-systems/berkeleys-algorithm/)
- [Lamport Logical Clock Algorithm](https://www.geeksforgeeks.org/dsa/lamports-logical-clock/)
- [Vector Clocks](https://en.wikipedia.org/wiki/Vector_clock)
- [Network Time Protocol](https://en.wikipedia.org/wiki/Network_Time_Protocol)

## License

MIT License
