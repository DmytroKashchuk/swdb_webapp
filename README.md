# SpiceWork Database API (swdb)

The API access to SpiceWork Database! A RESTful API for managing spice inventory with full CRUD operations.

## Features

- ✅ RESTful API with JSON responses
- ✅ SQLite database for persistent storage
- ✅ Full CRUD operations for spice management
- ✅ Search functionality
- ✅ CORS enabled for web applications
- ✅ Environment-based configuration
- ✅ Error handling and validation

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DmytroKashchuk/swdb.git
cd swdb
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
cp .env.example .env
```

4. Run the API:
```bash
python api.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### Root & Health

- `GET /` - API information and available endpoints
- `GET /health` - Health check

### Spices Management

- `GET /spices` - Get all spices
- `GET /spices/<id>` - Get spice by ID
- `POST /spices` - Create a new spice
- `PUT /spices/<id>` - Update a spice
- `DELETE /spices/<id>` - Delete a spice
- `GET /spices/search?q=<query>` - Search spices

## Usage Examples

### Get API Information
```bash
curl http://localhost:5000/
```

### Create a Spice
```bash
curl -X POST http://localhost:5000/spices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paprika",
    "origin": "Hungary",
    "heat_level": 2,
    "quantity": 100,
    "unit": "grams",
    "description": "Sweet and mild pepper powder"
  }'
```

### Get All Spices
```bash
curl http://localhost:5000/spices
```

### Get Specific Spice
```bash
curl http://localhost:5000/spices/1
```

### Update a Spice
```bash
curl -X PUT http://localhost:5000/spices/1 \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 150,
    "description": "Sweet and mild Hungarian pepper powder"
  }'
```

### Search Spices
```bash
curl "http://localhost:5000/spices/search?q=pepper"
```

### Delete a Spice
```bash
curl -X DELETE http://localhost:5000/spices/1
```

## Data Model

### Spice Object

```json
{
  "id": 1,
  "name": "Paprika",
  "origin": "Hungary",
  "heat_level": 2,
  "quantity": 100.0,
  "unit": "grams",
  "description": "Sweet and mild pepper powder",
  "created_at": "2025-11-10 19:53:00"
}
```

### Fields

- `id` (integer): Unique identifier (auto-generated)
- `name` (string, required): Name of the spice
- `origin` (string, optional): Country or region of origin
- `heat_level` (integer, optional): Heat level on scale of 0-10
- `quantity` (float, optional): Quantity in stock
- `unit` (string, optional): Unit of measurement (grams, oz, etc.)
- `description` (string, optional): Description of the spice
- `created_at` (timestamp): Creation timestamp (auto-generated)

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "count": 10  // for list endpoints
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## Configuration

Environment variables can be set in `.env` file:

- `DATABASE_PATH` - Path to SQLite database file (default: `spicework.db`)
- `API_HOST` - Host to bind the API (default: `0.0.0.0`)
- `API_PORT` - Port to run the API (default: `5000`)
- `FLASK_ENV` - Environment mode (development/production)

## Database

The API uses SQLite for data storage. The database file is automatically created on first run. The schema includes:

- **spices** table with fields for managing spice inventory
- Automatic timestamp tracking
- Unique constraint on spice names

## Development

### Project Structure

```
swdb/
├── api.py              # Flask API application
├── database.py         # Database operations
├── requirements.txt    # Python dependencies
├── .env.example       # Example environment configuration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

### Adding Features

The codebase is modular and easy to extend:

- Add new database operations in `database.py`
- Add new API endpoints in `api.py`
- Follow RESTful conventions

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
