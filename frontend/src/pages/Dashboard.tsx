import React, { useState, useEffect } from "react";
import { fetchMessages } from "../services/api";
import { Button } from "@/components/ui/ui/button";
import { Input } from "@/components/ui/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/ui/table";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/ui/card";
import { formatDistanceToNow, parseISO } from "date-fns";
import {
  FunnelIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  NoSymbolIcon, // For NO_NONVEG
  BeakerIcon, // For NO_DRINKING (replacing WineBottleIcon)
  FireIcon, // For NO_SMOKING
  UserGroupIcon, // For NO_BOYS
  CheckCircleIcon,
} from "@heroicons/react/20/solid";

interface Message {
  id: number;
  raw_text: string;
  time_created: string;
  author: string;
  details: {
    BHK: number;
    Bedroom: string;
    Sharing: boolean;
    Gender: string[];
    Address: string;
    Rent: number | string;
    Restrictions: string[];
    Furnished: string;
    Deposit: number | string;
    Brokerage: number;
    AvailableDate: string;
    ContactDetail: string;
  };
}

const Dashboard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showFullText, setShowFullText] = useState<boolean>(false);
  const [filters, setFilters] = useState<{
    BHK: number | null;
    Bedroom: string;
    Sharing: string; // "true", "false", or "" for no filter
    Gender: string;
    Address: string;
    Rent: number | null;
    Deposit: number | null;
    Restrictions: string;
    Furnished: string;
    Brokerage: number | null;
    AvailableDate: string;
    time_created: string;
    author: string;
    Contact: string;
  }>({
    BHK: null,
    Bedroom: "",
    Sharing: "",
    Gender: "",
    Address: "",
    Rent: null,
    Deposit: null,
    Restrictions: "",
    Furnished: "",
    Brokerage: null,
    AvailableDate: "",
    time_created: "",
    author: "",
    Contact: "",
  });
  const [filterVisibility, setFilterVisibility] = useState<{
    BHK: boolean;
    Bedroom: boolean;
    Sharing: boolean;
    Gender: boolean;
    Address: boolean;
    Rent: boolean;
    Deposit: boolean;
    Restrictions: boolean;
    Furnished: boolean;
    Brokerage: boolean;
    AvailableDate: boolean;
    time_created: boolean;
    author: boolean;
    Contact: boolean;
  }>({
    BHK: false,
    Bedroom: false,
    Sharing: false,
    Gender: false,
    Address: false,
    Rent: false,
    Deposit: false,
    Restrictions: false,
    Furnished: false,
    Brokerage: false,
    AvailableDate: false,
    time_created: false,
    author: false,
    Contact: false,
  });

  useEffect(() => {
    const loadMessages = async () => {
      try {
        const data = await fetchMessages();
        setMessages(data);
        setLoading(false);
      } catch (error) {
        console.error("Failed to load messages:", error);
        setLoading(false);
      }
    };
    loadMessages();
  }, []);

  // Function to trim text to a fixed length
  const trimText = (text: string, maxLength: number = 50): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  // Function to get relative time
  const getRelativeTime = (time: string): string => {
    return formatDistanceToNow(parseISO(time), { addSuffix: true });
  };

  // Function to filter messages
  const filteredMessages = messages.filter((msg) => {
    // console.log(msg.details.Gender);
    // console.log(filters.Gender);

    console.log(msg.details.Sharing);
    console.log(filters.Sharing);
    return (
      (filters.BHK === null || msg.details.BHK === filters.BHK) &&
      (filters.Bedroom === "" ||
        (filters.Bedroom === "Hall" && msg.details.Bedroom === "Hall") ||
        (filters.Bedroom === "Non-master Bedroom" &&
          msg.details.Bedroom === "Non-master Bedroom") ||
        (filters.Bedroom === "Master Bedroom" &&
          msg.details.Bedroom === "Master Bedroom") ||
        (filters.Bedroom === "Single" && msg.details.Bedroom === "Single") ||
        (filters.Bedroom === "Double" && msg.details.Bedroom === "Double")) &&
      (filters.Sharing === "" ||
        (filters.Sharing === "true" && msg.details.Sharing) ||
        (filters.Sharing === "false" && !msg.details.Sharing)) &&
      (filters.Gender === "" ||
        (filters.Gender === "Male" && msg.details.Gender.includes("Male")) ||
        (filters.Gender === "Female" &&
          msg.details.Gender.includes("Female")) ||
        (filters.Gender === "Family" &&
          msg.details.Gender.includes("Family"))) &&
      (filters.Address === "" ||
        msg.details.Address.toLowerCase().includes(
          filters.Address.toLowerCase()
        )) &&
      (filters.Rent === null || msg.details.Rent === filters.Rent) &&
      (filters.Deposit === null || msg.details.Deposit === filters.Deposit) &&
      (filters.Restrictions === "" ||
        (filters.Restrictions === "NONE" &&
          msg.details.Restrictions.includes("NONE")) ||
        (filters.Restrictions === "NO_SMOKING" &&
          msg.details.Restrictions.includes("NO_SMOKING")) ||
        (filters.Restrictions === "NO_DRINKING" &&
          msg.details.Restrictions.includes("NO_DRINKING")) ||
        (filters.Restrictions === "NO_NONVEG" &&
          msg.details.Restrictions.includes("NO_NONVEG")) ||
        (filters.Restrictions === "NO_BOYS" &&
          msg.details.Restrictions.includes("NO_BOYS"))) &&
      (filters.Furnished === "" ||
        (filters.Furnished === "FURNISHED" &&
          msg.details.Furnished === "FURNISHED") ||
        (filters.Furnished === "UNFURNISHED" &&
          msg.details.Furnished === "UNFURNISHED") ||
        (filters.Furnished === "SEMIFURNISHED" &&
          msg.details.Furnished === "SEMIFURNISHED")) &&
      (filters.Brokerage === null ||
        msg.details.Brokerage === filters.Brokerage) &&
      (filters.AvailableDate === "" ||
        msg.details.AvailableDate.toLowerCase().includes(
          filters.AvailableDate.toLowerCase()
        )) &&
      (filters.time_created === "" ||
        getRelativeTime(msg.time_created)
          .toLowerCase()
          .includes(filters.time_created.toLowerCase())) &&
      (filters.author === "" ||
        msg.author.toLowerCase().includes(filters.author.toLowerCase()))
    );
  });

  // Handler to update string filter values
  const handleStringFilterChange =
    (column: keyof typeof filters) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setFilters((prev) => ({
        ...prev,
        [column]: e.target.value,
      }));
    };

  // Handler to update number filter values
  const handleNumberFilterChange =
    (column: keyof typeof filters) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value === "" ? null : Number(e.target.value);
      setFilters((prev) => ({
        ...prev,
        [column]: value,
      }));
    };

  // Handler to update Sharing filter (boolean via select)
  const handleStaticFilterChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handler to toggle filter input visibility
  const toggleFilterVisibility = (column: keyof typeof filterVisibility) => {
    setFilterVisibility((prev) => ({
      ...prev,
      [column]: !prev[column],
    }));
  };

  const genderStyles = {
    Male: "bg-green-100 text-blue-800",
    Female: "bg-red-100 text-red-800",
    Family: "bg-blue-100 text-green-800",
  } as const;

  // Ensure only valid keys are used
  const getGenderStyle = (gender: string): string =>
    genderStyles[gender as keyof typeof genderStyles] ||
    "bg-gray-100 text-gray-800";

  const bedroomStyles = {
    Hall: "bg-green-100 text-green-800",
    "Non-master Bedroom": "bg-red-100 text-red-800",
    Single: "bg-red-100 text-red-800",
    "Master Bedroom": "bg-blue-100 text-blue-800",
    Double: "bg-blue-100 text-blue-800",
  } as const;

  // Ensure only valid keys are used
  const getBedroomStyle = (bedroom: string): string =>
    bedroomStyles[bedroom as keyof typeof bedroomStyles] ||
    "bg-gray-100 text-gray-800";

  const furnishedStyles = {
    SEMI_FURNISHED: "bg-blue-100 text-blue-800",
    FURNISHED: "bg-green-100 text-green-800",
    UNFURNISHED: "bg-red-100 text-red-800",
  } as const;

  // Ensure only valid keys are used
  const getFurnishedStyle = (furnish: string): string =>
    furnishedStyles[furnish as keyof typeof furnishedStyles] ||
    "bg-gray-100 text-gray-800";

  const getRestrictionDisplay = (restriction: string) => {
    switch (restriction.toUpperCase()) {
      case "NO_NONVEG":
        return (
          <NoSymbolIcon className="w-5 h-5 text-red-600" title="No Non-Veg" />
        );
      case "NO_DRINKING":
        return (
          <BeakerIcon className="w-5 h-5 text-red-600" title="No Drinking" />
        );
      case "NO_SMOKING":
        return <FireIcon className="w-5 h-5 text-red-600" title="No Smoking" />;
      case "NO_BOYS":
        return (
          <UserGroupIcon className="w-5 h-5 text-red-600" title="No Boys" />
        );
      case "NONE":
        return (
          <CheckCircleIcon
            className="w-5 h-5 text-green-600"
            title="No Restrictions"
          />
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {restriction}
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Bar */}
      <nav className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-white text-2xl font-semibold tracking-tight">
            Telegram Messages Dashboard
          </h1>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto p-6">
        <Card className="mb-6 border-none shadow-lg rounded-xl overflow-hidden">
          <CardHeader className="bg-gray-50 border-b">
            <CardTitle className="text-2xl font-semibold text-gray-800">
              Recent Messages
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {loading ? (
              <div className="flex justify-center items-center py-10">
                <div className="w-6 h-6 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="ml-3 text-gray-600 text-lg">
                  Loading messages...
                </span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table className="w-full">
                  <TableHeader className="bg-gray-50">
                    <TableRow className="border-b border-gray-200">
                      <TableHead className="w-[100px] font-semibold text-gray-700 py-4">
                        ID
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>BHK</span>
                          <button onClick={() => toggleFilterVisibility("BHK")}>
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.BHK && (
                          <Input
                            type="number"
                            placeholder="Filter BHK..."
                            value={filters.BHK ?? ""}
                            onChange={handleNumberFilterChange("BHK")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Occupancy</span>
                          <button
                            onClick={() => toggleFilterVisibility("Bedroom")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Bedroom && (
                          <select
                            name="Bedroom"
                            value={filters.Bedroom}
                            onChange={handleStaticFilterChange}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all w-full"
                          >
                            <option value="">All</option>
                            <option value="Hall">Hall</option>
                            <option value="Non-master Bedroom">
                              Non-Master
                            </option>
                            <option value="Master Bedroom">Master</option>
                            <option value="Single">Single</option>
                            <option value="Double">Double</option>
                          </select>
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Sharing</span>
                          <button
                            onClick={() => toggleFilterVisibility("Sharing")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Sharing && (
                          <select
                            name="Sharing"
                            value={filters.Sharing}
                            onChange={handleStaticFilterChange}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all w-full"
                          >
                            <option value="">All</option>
                            <option value="true">True</option>
                            <option value="false">False</option>
                          </select>
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Gender</span>
                          <button
                            onClick={() => toggleFilterVisibility("Gender")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Gender && (
                          <select
                            name="Gender"
                            value={filters.Gender}
                            onChange={handleStaticFilterChange}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all w-full"
                          >
                            <option value="">All</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Family">Family</option>
                          </select>
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Address</span>
                          <button
                            onClick={() => toggleFilterVisibility("Address")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Address && (
                          <Input
                            placeholder="Filter Address..."
                            value={filters.Address}
                            onChange={handleStringFilterChange("Address")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Rent</span>
                          <button
                            onClick={() => toggleFilterVisibility("Rent")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Rent && (
                          <Input
                            type="number"
                            placeholder="Filter Rent..."
                            value={filters.Rent ?? ""}
                            onChange={handleNumberFilterChange("Rent")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Deposit</span>
                          <button
                            onClick={() => toggleFilterVisibility("Deposit")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Deposit && (
                          <Input
                            type="number"
                            placeholder="Filter Deposit..."
                            value={filters.Deposit ?? ""}
                            onChange={handleNumberFilterChange("Deposit")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Restrictions</span>
                          <button
                            onClick={() =>
                              toggleFilterVisibility("Restrictions")
                            }
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Restrictions && (
                          <select
                            name="Restrictions"
                            value={filters.Restrictions}
                            onChange={handleStaticFilterChange}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all w-full"
                          >
                            <option value="">All</option>
                            <option value="NONE">None</option>
                            <option value="NO_SMOKING">No Smoking</option>
                            <option value="NO_DRINKING">No Drinking</option>
                            <option value="NO_BOYS">No Boys</option>
                            <option value="NO_NONVEG">No Non-Veg</option>
                          </select>
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Furnished</span>
                          <button
                            onClick={() => toggleFilterVisibility("Furnished")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Furnished && (
                          <select
                            name="Furnished"
                            value={filters.Furnished}
                            onChange={handleStaticFilterChange}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all w-full"
                          >
                            <option value="">All</option>
                            <option value="FURNISHED">Furnished</option>
                            <option value="SEMI_FURNISHED">
                              Semi-Furnished
                            </option>
                            <option value="UNFURNISHED">Unfurnished</option>
                          </select>
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Brokerage</span>
                          <button
                            onClick={() => toggleFilterVisibility("Brokerage")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.Brokerage && (
                          <Input
                            type="number"
                            placeholder="Filter Brokerage..."
                            value={filters.Brokerage ?? ""}
                            onChange={handleNumberFilterChange("Brokerage")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>AvailableDate</span>
                          <button
                            onClick={() =>
                              toggleFilterVisibility("AvailableDate")
                            }
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.AvailableDate && (
                          <Input
                            placeholder="Filter Available Date..."
                            value={filters.AvailableDate}
                            onChange={handleStringFilterChange("AvailableDate")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Time</span>
                          <button
                            onClick={() =>
                              toggleFilterVisibility("time_created")
                            }
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.time_created && (
                          <Input
                            placeholder="Filter Time Created..."
                            value={filters.time_created}
                            onChange={handleStringFilterChange("time_created")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>Contact</span>
                        </div>
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        Text
                      </TableHead>
                      <TableHead className="font-semibold text-gray-700 py-4">
                        <div className="flex items-center space-x-2">
                          <span>SenderName</span>
                          <button
                            onClick={() => toggleFilterVisibility("author")}
                          >
                            <FunnelIcon className="w-4 h-4 text-gray-500 hover:text-indigo-600 transition-colors" />
                          </button>
                        </div>
                        {filterVisibility.author && (
                          <Input
                            placeholder="Filter Author..."
                            value={filters.author}
                            onChange={handleStringFilterChange("author")}
                            className="mt-2 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-200 transition-all"
                          />
                        )}
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredMessages.length === 0 ? (
                      <TableRow>
                        <TableCell
                          colSpan={15}
                          className="text-center py-10 text-gray-500 italic"
                        >
                          No matching messages found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredMessages.map((msg) => (
                        <TableRow
                          key={msg.id}
                          className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                        >
                          <TableCell className="font-medium text-gray-900 py-4">
                            {msg.id}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.BHK}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBedroomStyle(
                                msg.details.Bedroom
                              )}`}
                            >
                              {msg.details.Bedroom.replace("Bedroom", "")}
                            </span>
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.Sharing ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Yes
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                No
                              </span>
                            )}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            <div className="flex flex-wrap gap-2">
                              {Array.isArray(msg.details.Gender) ? (
                                msg.details.Gender.map((gender, index) => (
                                  <span
                                    key={index}
                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getGenderStyle(
                                      gender
                                    )}`}
                                  >
                                    {gender}
                                  </span>
                                ))
                              ) : (
                                <span
                                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getGenderStyle(
                                    msg.details.Gender
                                  )}`}
                                >
                                  {msg.details.Gender}
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.Address}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.Rent
                              ? `₹${msg.details.Rent.toLocaleString()}`
                              : "-"}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.Deposit
                              ? `₹${msg.details.Deposit.toLocaleString()}`
                              : "-"}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            <div className="flex flex-wrap gap-2">
                              {Array.isArray(msg.details.Restrictions)
                                ? msg.details.Restrictions.map(
                                    (restriction, index) => (
                                      <span key={index}>
                                        {getRestrictionDisplay(restriction)}
                                      </span>
                                    )
                                  )
                                : getRestrictionDisplay(
                                    msg.details.Restrictions
                                  )}
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getFurnishedStyle(
                                msg.details.Furnished
                              )}`}
                            >
                              {msg.details.Furnished.replace("_", "")}
                            </span>
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.Brokerage
                              ? `₹${msg.details.Brokerage.toLocaleString()}`
                              : "-"}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.AvailableDate}
                          </TableCell>
                          <TableCell className="text-gray-600 py-4 relative group cursor-pointer">
                            <span className="block">
                              {getRelativeTime(msg.time_created)}
                            </span>
                            <span className="absolute left-0 top-full mt-2 p-2 bg-gray-800 text-white text-sm rounded-lg invisible group-hover:visible z-10 whitespace-normal max-w-xs shadow-lg">
                              {new Date(
                                Date.parse(msg.time_created)
                              ).toLocaleString()}
                            </span>
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.details.ContactDetail}
                          </TableCell>
                          <TableCell
                            className="text-gray-800 py-4 relative group cursor-pointer"
                            onClick={() => setShowFullText(!showFullText)}
                          >
                            <span
                              className={
                                showFullText
                                  ? "whitespace-normal"
                                  : "truncate block max-w-[200px]"
                              }
                            >
                              {showFullText
                                ? msg.raw_text
                                : trimText(msg.raw_text, 50)}
                            </span>
                            <span className="absolute left-0 top-full mt-2 p-2 bg-gray-800 text-white text-sm rounded-lg invisible group-hover:visible z-10 whitespace-normal max-w-xs shadow-lg">
                              {msg.raw_text}
                            </span>
                          </TableCell>
                          <TableCell className="text-gray-600 py-4">
                            {msg.author}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        <div className="flex justify-center items-center space-x-4">
          <Button
            variant="outline"
            disabled
            className="rounded-lg border-gray-300 text-gray-700 hover:bg-gray-100 transition-all"
          >
            Previous
          </Button>
          <span className="text-gray-600 font-medium">Page 1 of 10</span>
          <Button
            variant="outline"
            className="rounded-lg border-gray-300 text-gray-700 hover:bg-gray-100 transition-all"
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
