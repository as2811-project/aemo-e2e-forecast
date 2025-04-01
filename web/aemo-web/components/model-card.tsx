"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { fetchModelMetadata } from "@/app/actions/fetchModelMetadata";
import { GripIcon } from "./meta-loader";

interface ModelMetric {
  key: string;
  value: string | number;
  description?: string;
}

interface ModelMetadata {
  version: number;
  training_samples: number;
  rmse: number;
  mae: number;
  r2: number;
  feature_columns: string;
  training_date: string;
  training_week: number;
}

export default function ModelCard() {
  const [metadata, setMetadata] = useState<ModelMetadata | null>(null);

  useEffect(() => {
    async function loadMetadata() {
      const response = await fetchModelMetadata();
      if (response && response.statusCode === 200) {
        setMetadata(JSON.parse(response.body));
      }
    }
    loadMetadata();
  }, []);

  if (!metadata) {
    return (
      <div>
        <GripIcon />
      </div>
    );
  }

  const metrics: ModelMetric[] = [
    {
      key: "Training Samples",
      value: metadata.training_samples,
      description: "Number of samples used for training",
    },
    {
      key: "RMSE",
      value: metadata.rmse.toFixed(4),
      description: "Root Mean Square Error",
    },
    {
      key: "MAE",
      value: metadata.mae.toFixed(4),
      description: "Mean Absolute Error",
    },
    {
      key: "R²",
      value: metadata.r2.toFixed(3),
      description: "Coefficient of determination",
    },
    {
      key: "Training Date",
      value: new Date(metadata.training_date).toLocaleString("en-AU"),
      description: "Timestamp of last training",
    },
    {
      key: "Features",
      value: JSON.parse(metadata.feature_columns).length,
      description: "Number of features used in the model",
    },
  ];

  return (
    <Card className="w-full max-w-3xl mt-2">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-xl font-medium">Model Card</CardTitle>
          <Badge variant="outline" className="px-3 py-1 text-xs font-medium">
            v{metadata.version}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <div className="text-sm font-medium text-muted-foreground">
            Model Family
          </div>
          <div className="mt-1 text-lg font-semibold">XGBoost</div>
        </div>

        <Separator className="my-4" />

        <div className="grid gap-4 sm:grid-cols-2">
          {metrics.map((metric) => (
            <div key={metric.key} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium text-muted-foreground">
                  {metric.key}
                </div>
                <div className="font-mono text-sm font-medium">
                  {metric.value}
                </div>
              </div>
              {metric.description && (
                <div className="text-xs text-muted-foreground">
                  {metric.description}
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
