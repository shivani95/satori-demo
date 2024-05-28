# satori-demo


Commands to run locally 
python app.py

https://zoom.us/oauth/authorize?response_type=code&client_id=PWUduPaDSyy7LmF8GxDQHA&redirect_uri=http://localhost:5000/oauth/callback

curl -X POST http://localhost:5000/webhook \
-H "Content-Type: application/json" \
-d '{
  "event": "recording.completed",
  "payload": {
    "object": {
      "id": "88135280073"
    }
  }
}'

