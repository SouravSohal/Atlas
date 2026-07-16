import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { useGlobalStore } from "../store/useGlobalStore";
import { AuthTab } from "../features/settings/components/AuthTab";

describe("Authentication & Session context verification tests", () => {
  beforeEach(() => {
    useGlobalStore.setState({
      accessToken: "mock-firebase-id-token",
      user: {
        name: "Test Operations Director",
        email: "director@atlas.ai",
        role: "Medical Coordinator",
      },
      userRole: "Medical Coordinator",
      sessionExpiry: "12 Hours",
    });
  });

  it("should retrieve correctly current user name and role from global store", () => {
    const state = useGlobalStore.getState();
    expect(state.accessToken).toBe("mock-firebase-id-token");
    expect(state.user.name).toBe("Test Operations Director");
    expect(state.userRole).toBe("Medical Coordinator");
  });

  it("should display current authentication credentials and session details in AuthTab page", () => {
    render(
      <AuthTab
        userRole="Medical Coordinator"
        sessionExpiry="12 Hours"
      />
    );

    expect(screen.getByText("Identity & Authentication Settings")).toBeInTheDocument();
    expect(screen.getByText("Medical Coordinator")).toBeInTheDocument();
    expect(screen.getByText(/12 Hours/i)).toBeInTheDocument();
  });
});
