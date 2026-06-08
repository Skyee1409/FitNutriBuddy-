import json
import traceback
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from concurrent.futures import ThreadPoolExecutor

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

def get_client(model_id):
    if not settings.WATSONX_APIKEY or not settings.WATSONX_PROJECT_ID:
        raise ValueError("WATSONX_APIKEY and WATSONX_PROJECT_ID must be set in environment variables.")
    credentials = Credentials(
        url=settings.WATSONX_URL,
        api_key=settings.WATSONX_APIKEY
    )
    return ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=settings.WATSONX_PROJECT_ID,
        validate=False,   # skip model-spec GET call that causes 403
    )

def parse_body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}

def build_profile_context(profile: dict) -> str:
    return f"""User Profile:
Name: {profile.get('name', 'User')}, Age: {profile.get('age', '—')}, Gender: {profile.get('gender', '—')}
Height: {profile.get('height', '—')}cm, Weight: {profile.get('weight', '—')}kg, Target: {profile.get('target', '—')}kg, BMI: {profile.get('bmi', '—')}
Goal: {profile.get('goal', 'General fitness')}, Fitness Level: {profile.get('level', 'Beginner')}
Workout Types: {', '.join(profile.get('wtypes', [])) or 'any'}
Body Focus Areas: {', '.join(profile.get('areas', [])) or 'full body'}
Days/week: {profile.get('days', '3')}, Session: {profile.get('dur', '30-45 min')}
Equipment: {profile.get('equip', 'basic')}, Injuries: {profile.get('inj', 'none')}
Diet: {profile.get('diet', 'Non-vegetarian')}, Allergies: {', '.join(profile.get('allergies', [])) or 'none'}
Health Conditions: {', '.join(profile.get('health', [])) or 'none'}
Meals/day: {profile.get('meals', '3')}, Cuisine: {profile.get('cuis', 'Indian')}, Cook time: {profile.get('cook', '30 min')}
Sleep: {profile.get('sleep', '7hrs')}, Activity: {profile.get('act', 'moderate')}, Stress: {profile.get('stress', 'moderate')}
Workout time preference: {profile.get('wtime', 'morning')}, Extra notes: {profile.get('extra', 'none')}"""

BASE_SYSTEM = """You are FitNutriBuddy, an expert AI personal trainer and nutritionist.
Give detailed, personalized, practical advice. Use ** for bold headings and - for bullet points.
Be specific with sets, reps, calories, and foods. Be encouraging and concise."""

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    """General conversational AI endpoint."""

    def post(self, request):
        data = parse_body(request)
        messages = data.get('messages', [])
        profile = data.get('profile', {})

        if not messages:
            return JsonResponse({'error': 'No messages provided'}, status=400)

        profile_ctx = build_profile_context(profile) if profile else ''
        system = f"{BASE_SYSTEM}\n\n{profile_ctx}" if profile_ctx else BASE_SYSTEM

        # Detect if any message has an image block
        has_image = False
        for msg in messages:
            content = msg.get('content')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'image_url':
                        has_image = True
                        break
            if has_image:
                break

        # Sydney region only supports specific models; use Llama 3.3 70B Instruct
        model_id = "meta-llama/llama-3-3-70b-instruct"

        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)

        try:
            client = get_client(model_id=model_id)
            params = {
                GenParams.MAX_NEW_TOKENS: 2048,
                GenParams.TEMPERATURE: 0.7
            }
            response = client.chat(messages=formatted_messages, params=params)
            
            # Extract content and metadata
            reply = response['choices'][0]['message']['content']
            usage = response.get('usage', {})
            
            return JsonResponse({
                'reply': reply,
                'usage': {
                    'input_tokens': usage.get('prompt_tokens', 0),
                    'output_tokens': usage.get('completion_tokens', 0),
                }
            })
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GeneratePlanView(View):
    """Generate one specific plan section for a user."""

    PLAN_PROMPTS = {
        'weekly_workout': (
            "Generate a detailed 7-day weekly workout plan. Each day: day name, workout type, "
            "exercises with sets/reps/duration, intensity level, and a motivational tip. "
            "Include 1–2 rest days. Tailor to their fitness level, equipment, available time, injuries, and body area goals."
        ),
        'monthly_workout': (
            "Create a 4-week monthly workout progression plan. Each week: focus theme, intensity level, "
            "key exercises, and weekly goal. Show how difficulty and volume build week by week."
        ),
        'flexibility': (
            "Create a personalized flexibility and mobility routine: a daily 10-min morning stretch, "
            "a weekly yoga/flexibility session, and targeted stretches for their body focus areas. "
            "Include hold times and breathing cues."
        ),
        'weekly_diet': (
            "Generate a 7-day meal plan. Each day: breakfast, lunch, dinner, and snacks with approx calories. "
            "Consider diet type, allergies, cuisine preference, cooking time, health conditions, and fitness goal. "
            "Add a daily nutrition tip."
        ),
        'monthly_diet': (
            "Create a 4-week monthly nutrition plan. Each week: dietary focus, calorie targets, key foods to include, "
            "and nutrition goals. Show progression toward their target weight."
        ),
        'macros': (
            "Calculate and explain daily macro targets (protein, carbs, fat, total calories) for this user's profile. "
            "Include hydration goal, meal timing recommendations, top 5 food recommendations for their goal, "
            "and key supplement suggestions if relevant."
        ),
    }

    def post(self, request):
        data = parse_body(request)
        plan_type = data.get('plan_type', '')
        profile = data.get('profile', {})

        if plan_type not in self.PLAN_PROMPTS:
            return JsonResponse(
                {'error': f'Unknown plan_type. Choose from: {list(self.PLAN_PROMPTS.keys())}'},
                status=400
            )

        prompt = self.PLAN_PROMPTS[plan_type]
        profile_ctx = build_profile_context(profile)
        system = f"{BASE_SYSTEM}\n\n{profile_ctx}"

        formatted_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]

        try:
            client = get_client(model_id="meta-llama/llama-3-3-70b-instruct")
            params = {
                GenParams.MAX_NEW_TOKENS: 3000,
                GenParams.TEMPERATURE: 0.7
            }
            response = client.chat(messages=formatted_messages, params=params)
            
            return JsonResponse({
                'plan_type': plan_type,
                'content': response['choices'][0]['message']['content'],
            })
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GenerateAllPlansView(View):
    """Generate all 6 plans in parallel requests (called on profile completion)."""

    def post(self, request):
        data = parse_body(request)
        profile = data.get('profile', {})

        if not profile:
            return JsonResponse({'error': 'Profile data required'}, status=400)

        profile_ctx = build_profile_context(profile)
        system = f"{BASE_SYSTEM}\n\n{profile_ctx}"

        plan_prompts = {
            'weekly_workout': (
                "Generate a detailed 7-day weekly workout plan. Each day: day name, workout type, "
                "exercises with sets/reps/duration, intensity, tip. Include rest days. "
                "Match their level, equipment, time, injuries, and body area goals."
            ),
            'monthly_workout': (
                "Create a 4-week monthly workout progression. Each week: focus, intensity, key exercises, weekly goal."
            ),
            'flexibility': (
                "Create a personalized flexibility routine: daily 10-min stretch, weekly yoga session, "
                "targeted stretches for their focus areas. Include hold times and breathing cues."
            ),
            'weekly_diet': (
                "Generate a 7-day meal plan. Each day: breakfast, lunch, dinner, snacks with approx calories. "
                "Consider diet type, allergies, cuisine, cooking time, health conditions, goal."
            ),
            'monthly_diet': (
                "Create a 4-week monthly nutrition plan. Each week: focus, calorie targets, key foods, goal."
            ),
            'macros': (
                "Calculate daily macro targets (protein, carbs, fat, calories). Include hydration goal, "
                "meal timing, top 5 food recommendations, and supplement tips."
            ),
        }

        def generate_one_plan(plan_type, prompt):
            try:
                client = get_client(model_id="meta-llama/llama-3-3-70b-instruct")
                params = {
                    GenParams.MAX_NEW_TOKENS: 3000,
                    GenParams.TEMPERATURE: 0.7
                }
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
                response = client.chat(messages=messages, params=params)
                return plan_type, response['choices'][0]['message']['content'], None
            except Exception as e:
                return plan_type, None, str(e)

        results = {}
        errors = {}

        # Run all 6 requests concurrently in parallel threads to prevent gateway timeouts!
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(generate_one_plan, plan_type, prompt)
                for plan_type, prompt in plan_prompts.items()
            ]
            for future in futures:
                plan_type, content, err = future.result()
                if err:
                    errors[plan_type] = err
                else:
                    results[plan_type] = content

        return JsonResponse({
            'plans': results,
            'errors': errors,
            'profile_name': profile.get('name', 'User'),
        })

@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """Simple health check for IBM Cloud."""

    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'app': 'FitNutriBuddy',
            'version': '1.0.0',
            'api_configured': bool(settings.WATSONX_APIKEY and settings.WATSONX_PROJECT_ID),
        })


@method_decorator(csrf_exempt, name='dispatch')
class DebugView(View):
    """Debug endpoint — tests WatsonX connection and returns diagnostics."""

    def get(self, request):
        import sys
        diag = {
            'python_version': sys.version,
            'watsonx_url': settings.WATSONX_URL,
            'apikey_set': bool(settings.WATSONX_APIKEY),
            'apikey_preview': settings.WATSONX_APIKEY[:8] + '...' if settings.WATSONX_APIKEY else 'NOT SET',
            'project_id_set': bool(settings.WATSONX_PROJECT_ID),
            'project_id_preview': settings.WATSONX_PROJECT_ID[:8] + '...' if settings.WATSONX_PROJECT_ID else 'NOT SET',
            'sdk_version': None,
            'connection_test': None,
            'error': None,
        }
        try:
            import ibm_watsonx_ai
            diag['sdk_version'] = getattr(ibm_watsonx_ai, '__version__', 'unknown')
        except ImportError as e:
            diag['error'] = f'SDK not installed: {e}'
            return JsonResponse(diag, status=500)

        try:
            client = get_client(model_id='meta-llama/llama-3-3-70b-instruct')
            response = client.chat(
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': 'Reply with exactly: OK'}
                ],
                params={GenParams.MAX_NEW_TOKENS: 10, GenParams.TEMPERATURE: 0.1}
            )
            reply = response['choices'][0]['message']['content']
            diag['connection_test'] = f'SUCCESS — model replied: {reply.strip()[:100]}'
        except Exception as e:
            diag['connection_test'] = 'FAILED'
            diag['error'] = str(e)
            traceback.print_exc()

        status_code = 200 if diag['connection_test'] and 'SUCCESS' in diag['connection_test'] else 500
        return JsonResponse(diag, status=status_code)
