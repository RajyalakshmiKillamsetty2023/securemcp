# On Windows without make, run the commands directly (see README).
.PHONY: db db-stop api node lint test
db:
	docker compose up -d mongo
db-stop:
	docker compose down
api:
	cd backend && uvicorn app.main:app --reload --port 8000
node:
	cd api-node && npm run dev
lint:
	cd backend && ruff check .
test:
	cd backend && pytest -q
	cd api-node && npm test
