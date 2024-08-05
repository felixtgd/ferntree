import { Card } from "@tremor/react";
import { ModelFormDialog } from "./model-form-dialog";
import { ModelData } from "@/utils/definitions";

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
            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Models
                </h3>

                <div className="flex items-center">
                    <ModelFormDialog />
                </div>
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
