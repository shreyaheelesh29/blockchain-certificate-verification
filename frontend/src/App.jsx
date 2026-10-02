import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useNavigate,
  useParams
} from "react-router-dom";

import { useState, useEffect } from "react";


function Home() {
  return (
    <div className="page">
      <div className="container">

        <h1>🔗Certificate Verification System</h1>

        <p>
          Secure Certificate Issuance & Verification Using Blockchain Technology
        </p>

        <div className="home-actions">

          <Link
            to="/login"
            className="primary-button"
          >
            Admin Login
          </Link>

          <Link
            to="/verify/CERT-A99C4750FD"
            className="secondary-button"
          >
            Verify Certificate
          </Link>

        </div>

      </div>
    </div>
  );
}


function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const login = async (event) => {

    event.preventDefault();

    setLoading(true);
    setError("");


    try {

      const response = await fetch(
        "http://192.168.43.225:8000/auth/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            email,
            password
          })
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail || "Login failed."
        );

      }


      localStorage.setItem(
        "access_token",
        data.access_token
      );


      navigate("/dashboard");


    } catch (error) {

      setError(error.message);

    } finally {

      setLoading(false);

    }

  };


  return (

    <div className="page">

      <div className="form-card">

        <h1>Admin Login</h1>

        <p>
          Sign in to manage certificates.
        </p>


        <form onSubmit={login}>

          <label>Email</label>

          <input
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            placeholder="Enter email"
            required
          />


          <label>Password</label>

          <input
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            placeholder="Enter password"
            required
          />


          {error && (

            <div className="error-message">
              {error}
            </div>

          )}


          <button
            type="submit"
            className="verify-button"
            disabled={loading}
          >

            {loading
              ? "Signing in..."
              : "Login"}

          </button>

        </form>

      </div>

    </div>

  );
}


function Dashboard() {

  const navigate = useNavigate();


  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    navigate("/login");

  };


  return (

    <div className="page">

      <div className="dashboard-card">

        <div className="dashboard-header">

          <div>

            <h1>Admin Dashboard</h1>

            <p>
              Certificate Management
            </p>

          </div>


          <button
            className="logout-button"
            onClick={logout}
          >
            Logout
          </button>

        </div>
        
        <div className="stats-grid">

        <div className="stat-card">
          <h2>🔗</h2>
          <h3>Blockchain</h3>
          <p>Certificate Security</p>
        </div>

        <div className="stat-card">
          <h2>🛡️</h2>
          <h3>Verification</h3>
          <p>QR + Hash Validation</p>
        </div>

      </div>

        <div className="dashboard-actions">

          <button
            className="dashboard-action"
            onClick={() =>
              navigate("/create-certificate")
            }
          >

            <strong>
              Generate Certificate
            </strong>

            <span>
              Create and register a new certificate
            </span>

          </button>


          <Link
            to="/verify/CERT-A99C4750FD"
            className="dashboard-action"
          >

            <strong>
              Verify Certificate
            </strong>

            <span>
              Check certificate authenticity
            </span>

          </Link>

        </div>

      </div>

    </div>

  );
}


function CreateCertificate() {
  const [formData, setFormData] = useState({
    student_name: "",
    roll_number: "",
    course: "",
    institution: "",
    issue_date: ""
  });

  const [certificate, setCertificate] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setCertificate(null);

    try {
      const response = await fetch(
        "http://192.168.43.225:8000/certificates/create",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
          },
          body: JSON.stringify(formData)
        }
      );

      const data = await response.json();

      console.log("CERTIFICATE RESPONSE:", data);

      if (!response.ok) {
        alert(data.detail || "Certificate generation failed");
        return;
      }

      setCertificate(data);

    } catch (error) {
      console.error(error);
      alert("Unable to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">

      <div className="form-card">

        <h1>Generate Certificate</h1>

        <p>
          Create a blockchain-verified certificate.
        </p>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="student_name"
            placeholder="Student Name"
            value={formData.student_name}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="roll_number"
            placeholder="Roll Number"
            value={formData.roll_number}
            onChange={handleChange}
          />

          <input
            type="text"
            name="course"
            placeholder="Course"
            value={formData.course}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="institution"
            placeholder="Institution"
            value={formData.institution}
            onChange={handleChange}
            required
          />

          <input
            type="date"
            name="issue_date"
            value={formData.issue_date}
            onChange={handleChange}
            required
          />

          <button
            type="submit"
            className="primary-button full-button"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Certificate"}
          </button>

        </form>

        {certificate && (
          <div className="success-card">

            <h2>Certificate Generated Successfully 🎉</h2>

            <p>
              <strong>Certificate ID:</strong>{" "}
              {certificate.certificate_id}
            </p>

            <p>
              <strong>Status:</strong>{" "}
              {certificate.status}
            </p>

             <p>
                <strong>
                  Blockchain Transaction:
                </strong>{" "}
                Successfully Recorded ✅
              </p>

            <div className="button-row">

              <button
                className="primary-button"
                onClick={() =>
                  window.open(
                    `http://192.168.43.225:8000/generated-certificates/${certificate.certificate_id}.pdf`,
                    "_blank"
                  )
                }
              >
                Open Certificate
              </button>

              <button
                className="secondary-button"
                onClick={() =>
                  navigate(
                    `/verify/${certificate.certificate_id}`
                  )
                }
              >
                Verify Certificate
              </button>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}


function Verify() {
  const { certificateId } = useParams();

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkCertificateStatus = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `http://192.168.43.225:8000/verification/status/${certificateId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Certificate verification failed."
        );
      }

      setResult(data);

    } catch (error) {
      setResult({
        status: "ERROR",
        message: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const verifyCertificatePDF = async () => {
    if (!file) {
      setResult({
        status: "ERROR",
        message: "Please select a certificate PDF first."
      });

      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `http://192.168.43.225:8000/verification/verify?certificate_id=${certificateId}`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Verification failed."
        );
      }

      setResult(data);

    } catch (error) {
      setResult({
        status: "ERROR",
        message: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkCertificateStatus();
  }, [certificateId]);

  return (
    <div className="page">

      <div className="verification-card">

        <div className="verification-header">

          <div className="shield-icon">
            ✓
          </div>

          <h1>
            Verify Certificate
          </h1>

          <p>
            Check whether this certificate is
            authentic and registered on the
            blockchain.
          </p>

        </div>

        <div className="certificate-id-box">

          <span>
            Certificate ID
          </span>

          <strong>
            {certificateId}
          </strong>

        </div>

        {loading && (
          <div className="security-note">

            <strong>
              Checking Blockchain...
            </strong>

            <p>
              Verifying certificate status
              against the blockchain.
            </p>

          </div>
        )}

      {result && (

        <>

        <div className="verification-label">
      Verified Against Blockchain Record
        </div>

        <div
          className={`result-box result-${result.status.toLowerCase()}`}
        >

        <div className="result-status">

          {result.status === "VALID" && "✓"}
          {result.status === "INVALID" && "✕"}
          {result.status === "REVOKED" && "!"}
          {result.status === "ERROR" && "!"}

        </div>

        <div>

          <h2>{result.status}</h2>

          <p>{result.message}</p>

        </div>

      </div>

      </>

      )}

        {!loading &&
          result &&
          result.status !== "ERROR" &&
          result.status !== "REVOKED" && (

          <div className="upload-section">

            <label>
              Verify Actual Certificate PDF
            </label>

            <input
              type="file"
              accept=".pdf"
              onChange={(event) => {

                setFile(
                  event.target.files[0]
                );

              }}
            />

            {file && (

              <p className="selected-file">
                Selected: {file.name}
              </p>

            )}

            <button
              className="verify-button"
              onClick={verifyCertificatePDF}
              disabled={loading}
            >
              Verify PDF
            </button>

          </div>
        )}

        <div className="security-note">

          <strong>
            Blockchain Verification
          </strong>

          <p>
            Certificate status is checked against
            the blockchain record. Uploading the
            PDF performs an additional document
            hash verification.
          </p>

        </div>

      </div>

    </div>
  );
}


function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
          path="/create-certificate"
          element={<CreateCertificate />}
        />

        <Route
          path="/verify/:certificateId"
          element={<Verify />}
        />

      </Routes>

    </BrowserRouter>

  );

}


export default App;