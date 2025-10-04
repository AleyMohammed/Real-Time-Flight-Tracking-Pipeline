# Real-Time-Flight-Tracking-Pipeline
This project simulates a **real-time flight tracking system** (similar to AirRadar 2024) using a modern data engineering pipeline.   It generates fake flight events, streams them through Kafka, processes with Spark, stores in PostgreSQL, and visualizes with Streamlit.

---

# ✈️ Flight Radar 2024 - Real-Time Flight Tracking Pipeline

I built a project that simulates a **real-time flight tracking system** (like AirRadar 2024) using a modern data engineering pipeline.
I generated fake flight events, streamed them through Kafka, processed them with Spark, stored them in PostgreSQL, and visualized them using Streamlit.

---

## 🛠 Tools & Technologies

* **Python (Faker)** → I used it to generate fake flight data (Producer)
* **Kafka** → I used it as a message broker for real-time streaming
* **Spark (Structured Streaming)** → I processed and transformed flight events
* **Postgres** → I stored flight data here
* **Streamlit** → I built an interactive dashboard to visualize flight positions & statuses
* **Docker Compose** → I containerized all the services
<img width="434" height="443" alt="Image" src="https://github.com/user-attachments/assets/f5720ff2-aafe-4608-ad32-61a088593f94" />

---

## ▶️ How I Ran It

1. **I started the environment**

   ```bash
   docker-compose up -d
   ```

2. **I checked the containers**

   ```bash
   docker ps
   ```

3. **I ran the data producer**

   * I opened the `script/producer.ipynb` notebook in my **Anaconda environment**
   * I ran it to generate fake flight data and send events to Kafka topic `flights`.
<img width="1956" height="2534" alt="Image" src="https://github.com/user-attachments/assets/be6a8649-1d89-4129-8208-ff1785bdf26e" />

<img width="1419" height="624" alt="Image" src="https://github.com/user-attachments/assets/f66912d0-31f8-4bad-a828-0629ca351ad5" />

4. **I verified the Kafka topic**

   * I opened **Kafka UI** at [http://localhost:8090](http://localhost:8090)
   * I confirmed that topic `flights` was receiving messages
<img width="320" height="260" alt="Image" src="https://github.com/user-attachments/assets/c1331815-0782-4b8d-84f0-5be25662bb79" />

5. **I checked PostgreSQL**

   * I opened **pgAdmin** at [http://localhost:8085](http://localhost:8085)
   * I logged in with:

     * Email: `admin@admin.com`
     * Password: `admin`

6. **I created PostgreSQL connection**

   * In pgAdmin, I created a new server connection:

     * **Name**: `postgres_general`
     * **Host**: `postgres`
     * **Port**: `5432`
     * **Username**: `admin`
     * **Password**: `admin`

7. **I created the database**

   * I opened **Query Tool** in pgAdmin and ran:

     ```sql
     CREATE DATABASE flights_project;
     ```

8. **I created the flights table**

   * I connected to the `flights_project` database and ran:

     ```sql
     CREATE TABLE flights (
         flight_id VARCHAR PRIMARY KEY,
         origin TEXT,
         destination TEXT,
         status TEXT,
         departure_time BIGINT,
         arrival_time BIGINT
     );
     ```
<img width="1376" height="916" alt="Image" src="https://github.com/user-attachments/assets/6061e8cd-7ac8-4e0f-97b0-f524c81b3ba8" />

9. **I ran the Spark script**

   * I copied the Spark script from the `scripts` folder into a Jupyter Notebook
   * I accessed Jupyter at [http://localhost:8888](http://localhost:8888)
   * I installed PostgreSQL driver:

     ```bash
     pip install psycopg2-binary
     ```
   * I ran the notebook and confirmed that records were being inserted into PostgreSQL.
<img width="1584" height="831" alt="Image" src="https://github.com/user-attachments/assets/6deb278d-2324-4c32-b53d-c2cd8ae0c3c1" />


10. **I viewed the dashboard**

    * I opened the Streamlit app at [http://localhost:8501](http://localhost:8501)
    * I explored the **real-time flights map** and **flight statuses**.
   
    
<img width="1905" height="983" alt="Image" src="https://github.com/user-attachments/assets/b49df927-f123-494b-928d-5a394a764685" />


<img width="1894" height="900" alt="Image" src="https://github.com/user-attachments/assets/cfd27837-943f-48d5-9055-9c7346e653f6" />
---

## 📊 My Data Flow
![Image](https://github.com/user-attachments/assets/0a6f4d7e-d67b-4011-95af-1a87c5f3cc3c)
```
[ Python Producer (Faker) ]
            ↓
     Kafka Topic: flights
            ↓
   Spark Structured Streaming
            ↓
        PostgreSQL
            ↓
     Streamlit Dashboard
```

---

## 📝 Example Data

```json
{
  "flight_id": "FL1001",
  "origin": [40.6413, -73.7781],
  "destination": [51.4700, -0.4543],
  "status": "On Time",
  "departure_time": 1695638400,
  "arrival_time": 1695645600
}
```

---

## 🧹 How I Cleaned Up

To stop and remove containers, volumes, and networks:

```bash
docker-compose down -v
```

---

## 📌 Notes

* Kafka topic: **`flights`**
* Postgres DB: **flights_project**
* Streamlit UI shows flight map with status colors (On Time / Delayed / Cancelled).
* All services are containerized and orchestrated via **Docker Compose**.

---

