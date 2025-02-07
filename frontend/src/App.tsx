import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './view/Home';  // Assuming you have a Home component
import Profile from './view/user/Profile';
import About from './view/About';
import Login from './view/Login';
import Register from './view/Register';
import Dashboard from './view/user/Dashboard';
import AdminDashboard from './view/admin/AdminDashboard';  // Import AdminDashboard
import PrivateRoute from './component/PrivateRoute';
import ForgetPassword from './view/ForgetPassword';
import FAQPage from './view/admin/FAQPage';

const App = () => {
  return (
    <Router>
      <div>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />  {/* This is the new route for '/home' */}
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgetpassword" element={<ForgetPassword />} />


          {/* Protected Routes */}
          <Route path="/dashboard" element={<PrivateRoute element={<Dashboard />}  adminOnly={false} />} />
          <Route path="/profile" element={<PrivateRoute element={<Profile />}  adminOnly={false} />} />

          {/* Admin Protected Route */}
          <Route
            path="/admindashboard"
            element={<PrivateRoute element={<AdminDashboard />} adminOnly={true} />}  // Protect the AdminDashboard
          />
          <Route
            path="/faq"
            element={<PrivateRoute element={<FAQPage />} adminOnly={true} />}  // Protect the AdminDashboard
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
