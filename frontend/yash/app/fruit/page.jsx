"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { format } from "date-fns";
import { Qahiri } from "next/font/google";
                   
export default function FruitPage() {
  const [userFruits, setUserFruits] = useState([]);
  const [fruitName, setFruitName] = useState("");

  const addFruit = async () => {
    if (!fruitName.trim()) return alert("Enter a fruit name!");

    const newFruit = {
      name: fruitName,
      addedAt: new Date().toISOString(),
    };

    const res = await fetch("http://localhost:8000/fruits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newFruit),
    });

    if (res.ok) {
      setUserFruits([...userFruits, newFruit]);
      setFruitName("");
    } else {
      console.error("Failed to add fruit");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-5 space-y-8">
      <h1 className="text-3xl font-bold">Fruit Name    🍓</h1>

      {/* Input */}
      <div className="flex gap-2">:Array.from(document.querySelectorAll('selector')) 
        <input
          type="text"
          value={fruitName}
          onChange={(e) => setFruitName(e.target.value)}
          placeholder="Enter fruit name..."
          className="p-2 border rounded-md"
        />
        <Button onClick={addFruit} variant="destructive">
          Add Fruit
        </Button>
      </div>

      {/* Show list of added fruits */}
      {userFruits.length > 0 && (
        <ul className="w-1/3 bg-white p-4 rounded-lg shadow-md">
          {userFruits.map((fruit, idx) => (
            <li key={idx} className="p-2 border-b last:border-none">
              🍇 {fruit.name} —{" "}
              <span className="text-sm text-gray-500">
                {format(new Date(fruit.addedAt), "PPpp")}
              </span>
            </li>
          ))}
        </ul>
      )}

      {/* Carousel with added fruits only */}
      {userFruits.length > 0 && (
        <div className="w-full flex justify-center">
          <div className="w-full max-w-3xl">
            <Carousel>
              <CarouselContent>
                {userFruits.map((fruit, index) => (
                  <CarouselItem key={index}>
                    <div className="p-4 md:w-full">
                      <div className="h-full border-2 border-gray-200 border-opacity-60 rounded-lg overflow-hidden">
                        <img
                          className="lg:h-48 md:h-36 w-full object-cover object-center"
                          src={`https://source.unsplash.com/720x400/?${fruit.name},fruit`}
                          alt={fruit.name}
                        />
                        <div className="p-6">
                          <h2 className="tracking-widest text-xs title-font font-medium text-green-500 mb-1">
                            USER ADDED FRUIT
                          </h2>
                          <h1 className="title-font text-lg font-medium text-gray-900 mb-3">
                            {fruit.name}
                          </h1>
                          <p className="leading-relaxed text-sm text-gray-600 mb-3">
                            Added on: {format(new Date(fruit.addedAt), "PPpp")}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious />
              <CarouselNext />
            </Carousel>
          </div>
        </div>
      )}
    </div>
  );
}
