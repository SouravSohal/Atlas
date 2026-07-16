import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ActiveRecommendations } from "../features/mission-control/components/ActiveRecommendations";

describe("ActiveRecommendations Component tests", () => {
  const mockRecs = [
    {
      id: "rec-001",
      action_type: "reroute_crowds",
      priority: "high",
      confidence: 0.95,
      details: JSON.stringify({
        explanation: "Dynamic signage diversion at sector B.",
        why: "Crowd density limit breached.",
      }),
      status: "pending",
    },
  ];

  it("should render recommendation actions and confidence score", () => {
    const handleApprove = vi.fn();
    const handleSelectWhy = vi.fn();

    render(
      <ActiveRecommendations
        recs={mockRecs}
        approvedRecs={{}}
        setSelectedWhyRec={handleSelectWhy}
        handleApproveRecommendation={handleApprove}
      />
    );

    expect(screen.getByText("reroute_crowds")).toBeInTheDocument();
    expect(screen.getByText("95% Conf")).toBeInTheDocument();
    expect(screen.getByText("Dynamic signage diversion at sector B.")).toBeInTheDocument();
  });

  it("should trigger setSelectedWhyRec when Why is clicked", () => {
    const handleApprove = vi.fn();
    const handleSelectWhy = vi.fn();

    render(
      <ActiveRecommendations
        recs={mockRecs}
        approvedRecs={{}}
        setSelectedWhyRec={handleSelectWhy}
        handleApproveRecommendation={handleApprove}
      />
    );

    const whyBtn = screen.getByRole("button", { name: /Why\?/i });
    fireEvent.click(whyBtn);

    expect(handleSelectWhy).toHaveBeenCalledWith(mockRecs[0]);
  });

  it("should trigger handleApproveRecommendation when Approve is clicked", () => {
    const handleApprove = vi.fn();
    const handleSelectWhy = vi.fn();

    render(
      <ActiveRecommendations
        recs={mockRecs}
        approvedRecs={{}}
        setSelectedWhyRec={handleSelectWhy}
        handleApproveRecommendation={handleApprove}
      />
    );

    const approveBtn = screen.getByRole("button", { name: /Approve/i });
    fireEvent.click(approveBtn);

    expect(handleApprove).toHaveBeenCalledWith("rec-001");
  });

  it("should display Approved label if recommendation is approved", () => {
    const handleApprove = vi.fn();
    const handleSelectWhy = vi.fn();

    render(
      <ActiveRecommendations
        recs={mockRecs}
        approvedRecs={{ "rec-001": true }}
        setSelectedWhyRec={handleSelectWhy}
        handleApproveRecommendation={handleApprove}
      />
    );

    expect(screen.getByText("Approved")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Approve/i })).toBeNull();
  });
});
