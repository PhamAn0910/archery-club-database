import { useState } from "react";
import { Home } from "./components/Home";
import { LiveScoreEntry } from "./components/archer/LiveScoreEntry";
import { ScoreHistory } from "./components/archer/ScoreHistory";
import { PersonalBests } from "./components/archer/PersonalBests";
import { CompetitionResults } from "./components/archer/CompetitionResults";
import { ClubChampionship } from "./components/archer/ClubChampionship";
import { ScoreApproval } from "./components/recorder/ScoreApproval";
import { RecorderManagement } from "./components/recorder/AdminManagement";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Separator } from "./components/ui/separator";
import { mockArchers } from "./data/mockData";
import {
  Home as HomeIcon,
  Target,
  History,
  Trophy,
  Award,
  TrendingUp,
  CheckCircle,
  Settings,
  LogOut,
} from "lucide-react";

type UserRole = "guest" | "archer" | "recorder";
type Page =
  | "home"
  | "score-entry"
  | "my-scores"
  | "personal-bests"
  | "competitions"
  | "championship"
  | "score-approval"
  | "recorder-management";

function App() {
  const [userRole, setUserRole] = useState<UserRole>("guest");
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const [memberId, setMemberId] = useState("");
  const [currentArcher, setCurrentArcher] = useState<any>(null);

  const handleLogin = () => {
    if (!memberId.trim()) return;

    // Check if member ID exists
    const archer = mockArchers.find(
      (a) =>
        a.memberId.toLowerCase() ===
        memberId.trim().toLowerCase(),
    );

    if (archer) {
      setCurrentArcher(archer);
      // Check if user is a recorder (simplified - in real app would check a role field)
      // For demo, AV12345 is a recorder
      if (memberId.trim().toLowerCase() === "av12345") {
        setUserRole("recorder");
      } else {
        setUserRole("archer");
      }
    } else {
      alert("Member ID not found. Please check and try again.");
    }
  };

  const handleLogout = () => {
    setUserRole("guest");
    setCurrentArcher(null);
    setMemberId("");
    setCurrentPage("home");
  };

  const publicPages = [
    { id: "home" as Page, icon: HomeIcon, label: "Home" },
    {
      id: "competitions" as Page,
      icon: Award,
      label: "Competition Results",
    },
    {
      id: "championship" as Page,
      icon: TrendingUp,
      label: "Club Championship",
    },
  ];

  const archerPages = [
    {
      id: "score-entry" as Page,
      icon: Target,
      label: "Score Entry",
    },
    {
      id: "my-scores" as Page,
      icon: History,
      label: "My Scores",
    },
    {
      id: "personal-bests" as Page,
      icon: Trophy,
      label: "Personal Bests",
    },
  ];

  const recorderPages = [
    {
      id: "score-approval" as Page,
      icon: CheckCircle,
      label: "Approve Scores",
    },
    {
      id: "recorder-management" as Page,
      icon: Settings,
      label: "Manage Club",
    },
  ];

  const getAvailablePages = () => {
    const pages = [...publicPages];

    if (userRole === "archer") {
      pages.push(...archerPages);
    }

    if (userRole === "recorder") {
      pages.push(...recorderPages);
    }

    return pages;
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <Home />;
      case "score-entry":
        return currentArcher ? (
          <LiveScoreEntry archerName={currentArcher.fullName} />
        ) : (
          <div>Please log in</div>
        );
      case "my-scores":
        return currentArcher ? (
          <ScoreHistory archerId={currentArcher.id} />
        ) : (
          <div>Please log in</div>
        );
      case "personal-bests":
        return currentArcher ? (
          <PersonalBests archerId={currentArcher.id} />
        ) : (
          <div>Please log in</div>
        );
      case "competitions":
        return <CompetitionResults />;
      case "championship":
        return <ClubChampionship />;
      case "score-approval":
        return <ScoreApproval />;
      case "recorder-management":
        return <RecorderManagement />;
      default:
        return <Home />;
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Streamlit-style Sidebar */}
      <aside className="w-80 bg-muted border-r flex flex-col">
        {/* App Title */}
        <div className="p-6 border-b">
          <h1 className="text-center">Archery Club</h1>
        </div>

        {/* Login Section */}
        <div className="p-6 border-b">
          {userRole === "guest" ? (
            <div className="space-y-3">
              <div>
                <Label htmlFor="memberId">Member ID</Label>
                <Input
                  id="memberId"
                  value={memberId}
                  onChange={(e) => setMemberId(e.target.value)}
                  placeholder="Enter Member ID"
                  onKeyPress={(e) =>
                    e.key === "Enter" && handleLogin()
                  }
                />
              </div>
              <Button onClick={handleLogin} className="w-full">
                Login
              </Button>
              <p className="text-xs text-muted-foreground text-center">
                Demo: Try AV12345 (Recorder) or AV12346 (Archer)
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-3 bg-background rounded-lg">
                <div className="mb-1">Logged in as</div>
                <div>{currentArcher?.fullName}</div>
                <div className="text-muted-foreground">
                  {currentArcher?.memberId}
                </div>
              </div>
              <Button
                onClick={handleLogout}
                variant="outline"
                className="w-full"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {getAvailablePages().map((page) => {
            // Add separators before different sections
            const showSeparator =
              (page.id === "score-entry" &&
                userRole === "archer") ||
              (page.id === "score-approval" &&
                userRole === "recorder");

            return (
              <div key={page.id}>
                {showSeparator && (
                  <div className="py-2">
                    <Separator />
                    <div className="text-xs text-muted-foreground mt-2 px-2">
                      {page.id === "score-entry"
                        ? "Archer"
                        : "Recorder"}
                    </div>
                  </div>
                )}
                <button
                  onClick={() => setCurrentPage(page.id)}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left
                    ${currentPage === page.id ? "bg-primary text-primary-foreground" : "hover:bg-muted-foreground/10"}
                  `}
                >
                  <page.icon className="w-5 h-5 flex-shrink-0" />
                  <span>{page.label}</span>
                </button>
              </div>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t text-xs text-muted-foreground text-center">
          Archery Club Dashboard v2.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;