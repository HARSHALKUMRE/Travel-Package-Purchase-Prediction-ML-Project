from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run

from typing import Optional

from travel_pack.constants import APP_HOST, APP_PORT
from travel_pack.pipeline.prediction_pipeline import TravelData, TravelClassifier
from travel_pack.pipeline.training_pipeline import TrainPipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.Age: Optional[str] = None
        self.CityTier: Optional[str] = None
        self.DurationOfPitch: Optional[str] = None
        self.NumberOfPersonVisiting: Optional[str] = None
        self.NumberOfFollowups: Optional[str] = None
        self.PreferredPropertyStar: Optional[str] = None
        self.NumberOfTrips: Optional[str] = None
        self.Passport: Optional[str] = None
        self.PitchSatisfactionScore: Optional[str] = None
        self.OwnCar: Optional[str] = None
        self.NumberOfChildrenVisiting: Optional[str] = None
        self.MonthlyIncome: Optional[str] = None
        self.TypeofContact: Optional[str] = None
        self.Occupation: Optional[str] = None
        self.Gender: Optional[str] = None
        self.ProductPitched: Optional[str] = None
        self.MaritalStatus: Optional[str] = None
        self.Designation: Optional[str] = None
        
        
    async def get_travel_data(self):
        form = await self.request.form()
        self.Age = form.get("Age")
        self.CityTier = form.get("CityTier")
        self.DurationOfPitch = form.get("DurationOfPitch")
        self.NumberOfPersonVisiting = form.get("NumberOfPersonVisiting")
        self.NumberOfFollowups = form.get("NumberOfFollowups")
        self.PreferredPropertyStar = form.get("PreferredPropertyStar")
        self.NumberOfTrips = form.get("NumberOfTrips")
        self.Passport = form.get("Passport")
        self.PitchSatisfactionScore = form.get("PitchSatisfactionScore")
        self.OwnCar = form.get("OwnCar")
        self.NumberOfChildrenVisiting = form.get("NumberOfChildrenVisiting")
        self.MonthlyIncome = form.get("MonthlyIncome")
        self.TypeofContact = form.get("TypeofContact")
        self.Occupation = form.get("Occupation")
        self.Gender = form.get("Gender")
        self.ProductPitched = form.get("ProductPitched")
        self.MaritalStatus = form.get("MaritalStatus")
        self.Designation = form.get("Designation")
        
@app.get("/", tags=["authentication"])
async def index(request: Request):
    
    return templates.TemplateResponse(
        "index.html", {"request": request, "context": "Rendering"}
    )
    
    
@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()
        
        train_pipeline.run_pipeline()
        
        return Response("Training successful !!")
    
    except Exception as e:
        return Response(f"Error Occurred! {e}")
    
@app.post("/")
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)
        await form.get_travel_data()
        
        travel_data = TravelData(
            Age = form.Age,
            CityTier = form.CityTier,
            DurationOfPitch = form.DurationOfPitch,
            NumberOfPersonVisiting = form.NumberOfPersonVisiting,
            NumberOfFollowups = form.NumberOfFollowups,
            PreferredPropertyStar = form.PreferredPropertyStar,
            NumberOfTrips = form.NumberOfTrips,
            Passport = form.Passport,
            PitchSatisfactionScore = form.PitchSatisfactionScore,
            OwnCar = form.OwnCar,
            NumberOfChildrenVisiting = form.NumberOfChildrenVisiting,
            MonthlyIncome = form.MonthlyIncome,
            TypeofContact = form.TypeofContact,
            Occupation = form.Occupation,
            Gender = form.Gender,
            ProductPitched = form.ProductPitched,
            MaritalStatus = form.MaritalStatus,
            Designation = form.Designation,   
        )
        
        travel_df = travel_data.get_travel_input_data_frame()
        
        model_predictor = TravelClassifier()
        
        value = model_predictor.predict(dataframe=travel_df)[0]
        
        status = None
        if value == 1:
            status = "Package Purchased"
        else:
            status = "Package Not-Purchased"
            
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "context": status},
        )
        
    except Exception as e:
        return {"status": False, "error": f"{e}"}
    
    
if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)