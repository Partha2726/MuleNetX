import type { ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AccountSearch } from "./pages/AccountSearch";
import { AccountWorkspace } from "./pages/AccountWorkspace";
import { Login } from "./pages/Login";
import { NotFound } from "./pages/NotFound";
import { useSession } from "./state/session";

function RequireSession({ children }: { children: ReactNode }) {
  const token = useSession((st) => st.token);
  const location = useLocation();
  if (!token) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  return <>{children}</>;
}


export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <RequireSession>
            <Layout />
          </RequireSession>
        }
      >
        <Route path="accounts" element={<AccountSearch />} />
        <Route path="accounts/:id" element={<AccountWorkspace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
