import { Card } from "@tremor/react";

type ModelData = {
    model_name: string;
    location: string;
    roof_incl: number;
    roof_azimuth: number;
    electr_cons: number;
    peak_power: number;
    battery_cap: number;
};

async function ModelCard({modelData}: {modelData: ModelData}) {
    return (
        <Card
            className="flex flex-grow"
        >
            <h2>{modelData.model_name}</h2>
            <div className="flex flow-row">
                <div className="p-2">
                    <p>Location: {modelData.location}</p>
                    <p>Roof inclination: {modelData.roof_incl}°</p>
                    <p>Roof azimuth: {modelData.roof_azimuth}°</p>
                </div>
                <div className="p-2">
                    <p>Electricity consumption: {modelData.electr_cons} kWh</p>
                    <p>Peak power: {modelData.peak_power} kWp</p>
                    <p>Battery capacity: {modelData.battery_cap} kWh</p>
                </div>
            </div>
        </Card>
    );
}

export default async function Page() {
    return (
        <main>
            <div>
                <h1> Models </h1>
            </div>
            <div>
                <ModelCard modelData={{
                    model_name: "Model 1",
                    location: "Berlin",
                    roof_incl: 30,
                    roof_azimuth: 180,
                    electr_cons: 5000,
                    peak_power: 10,
                    battery_cap: 20,
                }} />
            </div>
        </main>
    );
}