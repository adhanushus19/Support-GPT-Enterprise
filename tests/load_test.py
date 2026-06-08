import random
import uuid
from locust import HttpUser, task, between

class SupportGPTExtendedUser(HttpUser):
    """
    Simulates concurrent customer chats and support agent approval reviews.
    """
    wait_time = between(1, 3)

    def on_start(self):
        """Pre-configure session identity credentials."""
        self.customer_id = f"cust_load_{random.randint(100, 999)}"
        self.session_id = str(uuid.uuid4())
        self.token = ""
        self.headers = {}
        self.user_setup()

    def user_setup(self):
        """Prepare JWT auth headers for simulating support agents."""
        username = f"agent_{uuid.uuid4().hex[:6]}"
        # Register and login agent to support authentication-locked approvals testing
        try:
            self.client.post("/auth/register", json={
                "username": username,
                "password": "loadtestpassword",
                "role": "agent"
            })
            login_res = self.client.post("/auth/token", json={
                "username": username,
                "password": "loadtestpassword"
            })
            if login_res.status_code == 200:
                self.token = login_res.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
        except Exception:
            pass

    @task(3)
    def check_health(self):
        """Ping API health endpoint."""
        self.client.get("/health")

    @task(5)
    def submit_chat_messages(self):
        """Submit support questions simulating customers."""
        questions = [
            "How do I submit a refund request?",
            "The API is returning timeout 504 errors.",
            "Can I change my account preferences verification email?",
            "What is the billing window limit?"
        ]
        self.client.post("/chat", json={
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "message": random.choice(questions),
            "kb_version": "v1"
        })

    @task(2)
    def list_tickets_and_profiles(self):
        """Retrieve historical cases and order summaries."""
        self.client.get("/tickets")
        self.client.post("/customer-context", json={
            "customer_id": self.customer_id
        })

    @task(1)
    def process_pending_approvals(self):
        """Simulate agent inspecting and approving response drafts."""
        if not self.headers:
            return
            
        list_res = self.client.get("/approvals/pending", headers=self.headers)
        if list_res.status_code == 200:
            approvals = list_res.json()
            if approvals:
                target = random.choice(approvals)
                self.client.post(f"/approvals/{target['id']}", json={
                    "approval_id": target["id"],
                    "modified_response": "Approved by automated load test.",
                    "status": "approved"
                }, headers=self.headers)
