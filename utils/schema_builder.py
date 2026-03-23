import os, json
from genson import SchemaBuilder

input_folder = "json_inputs/"
output_folder = "data/json_schema/"

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.endswith(".json"):
        builder = SchemaBuilder()
        with open(os.path.join(input_folder, file)) as f:
            data = json.load(f)
            builder.add_object(data)

        schema = builder.to_schema()

        out_file = file.replace(".json", "_schema.json")
        with open(os.path.join(output_folder, out_file), "w") as f:
            json.dump(schema, f, indent=2)

print("Schemas generated!")
