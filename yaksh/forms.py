from django import forms

from yaksh.models import (
    get_model_class, Profile, Quiz, Question, Course, QuestionPaper, Lesson,
    LearningModule, TestCase, languages, question_types, Post, Comment
)
from grades.models import GradingSystem
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from textwrap import dedent
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters
from string import punctuation, digits
import pytz
from .send_emails import generate_activation_key

languages = (("", "Select Language"),) + languages

question_types = (("", "Select Question Type"),) + question_types

test_case_types = (
    ("standardtestcase", "Standard Testcase"),
    ("stdiobasedtestcase", "StdIO Based Testcase"),
    ("mcqtestcase", "MCQ Testcase"),
    ("hooktestcase", "Hook Testcase"),
    ("integertestcase", "Integer Testcase"),
    ("stringtestcase", "String Testcase"),
    ("floattestcase", "Float Testcase"),
)

country_codes = (("DZ-213","Algeria (+213)")
,("AD-376","Andorra (+376)")
,("AO-244","Angola (+244)")
,("AI-1264","Anguilla (+1264)")
,("AG-1268","Antigua &amp; Barbuda (+1268)")
,("AR-54","Argentina (+54)")
,("AM-374","Armenia (+374)")
,("AW-297","Aruba (+297)")
,("AU-61","Australia (+61)")
,("AT-43","Austria (+43)")
,("AZ-994","Azerbaijan (+994)")
,("BS-1242","Bahamas (+1242)")
,("BH-973","Bahrain (+973)")
,("BD-880","Bangladesh (+880)")
,("BB-1246","Barbados (+1246)")
,("BY-375","Belarus (+375)")
,("BE-32","Belgium (+32)")
,("BZ-501","Belize (+501)")
,("BJ-229","Benin (+229)")
,("BM-1441","Bermuda (+1441)")
,("BT-975","Bhutan (+975)")
,("BO-591","Bolivia (+591)")
,("BA-387","Bosnia Herzegovina (+387)")
,("BW-267","Botswana (+267)")
,("BR-55","Brazil (+55)")
,("BN-673","Brunei (+673)")
,("BG-359","Bulgaria (+359)")
,("BF-226","Burkina Faso (+226)")
,("BI-257","Burundi (+257)")
,("KH-855","Cambodia (+855)")
,("CM-237","Cameroon (+237)")
,("CA-1","Canada (+1)")
,("CV-238","Cape Verde Islands (+238)")
,("KY-1345","Cayman Islands (+1345)")
,("CF-236","Central African Republic (+236)")
,("CL-56","Chile (+56)")
,("CN-86","China (+86)")
,("CO-57","Colombia (+57)")
,("KM-269","Comoros (+269)")
,("CG-242","Congo (+242)")
,("CK-682","Cook Islands (+682)")
,("CR-506","Costa Rica (+506)")
,("HR-385","Croatia (+385)")
,("CU-53","Cuba (+53)")
,("CY-90392","Cyprus North (+90392)")
,("CY-357","Cyprus South (+357)")
,("CZ-42","Czech Republic (+42)")
,("DK-45","Denmark (+45)")
,("DJ-253","Djibouti (+253)")
,("DM-1809","Dominica (+1809)")
,("DO-1809","Dominican Republic (+1809)")
,("EC-593","Ecuador (+593)")
,("EG-20","Egypt (+20)")
,("SV-503","El Salvador (+503)")
,("GQ-240","Equatorial Guinea (+240)")
,("ER-291","Eritrea (+291)")
,("EE-372","Estonia (+372)")
,("ET-251","Ethiopia (+251)")
,("FK-500","Falkland Islands (+500)")
,("FO-298","Faroe Islands (+298)")
,("FJ-679","Fiji (+679)")
,("FI-358","Finland (+358)")
,("FR-33","France (+33)")
,("GF-594","French Guiana (+594)")
,("PF-689","French Polynesia (+689)")
,("GA-241","Gabon (+241)")
,("GM-220","Gambia (+220)")
,("GE-7880","Georgia (+7880)")
,("DE-49","Germany (+49)")
,("GH-233","Ghana (+233)")
,("GI-350","Gibraltar (+350)")
,("GR-30","Greece (+30)")
,("GL-299","Greenland (+299)")
,("GD-1473","Grenada (+1473)")
,("GP-590","Guadeloupe (+590)")
,("GU-671","Guam (+671)")
,("GT-502","Guatemala (+502)")
,("GN-224","Guinea (+224)")
,("GW-245","Guinea - Bissau (+245)")
,("GY-592","Guyana (+592)")
,("HT-509","Haiti (+509)")
,("HN-504","Honduras (+504)")
,("HK-852","Hong Kong (+852)")
,("HU-36","Hungary (+36)")
,("IS-354","Iceland (+354)")
,("IN-91","India (+91)")
,("ID-62","Indonesia (+62)")
,("IR-98","Iran (+98)")
,("IQ-964","Iraq (+964)")
,("IE-353","Ireland (+353)")
,("IL-972","Israel (+972)")
,("IT-39","Italy (+39)")
,("JM-1876","Jamaica (+1876)")
,("JP-81","Japan (+81)")
,("JO-962","Jordan (+962)")
,("KZ-7","Kazakhstan (+7)")
,("KE-254","Kenya (+254)")
,("KI-686","Kiribati (+686)")
,("KP-850","Korea North (+850)")
,("KR-82","Korea South (+82)")
,("KW-965","Kuwait (+965)")
,("KG-996","Kyrgyzstan (+996)")
,("LA-856","Laos (+856)")
,("LV-371","Latvia (+371)")
,("LB-961","Lebanon (+961)")
,("LS-266","Lesotho (+266)")
,("LR-231","Liberia (+231)")
,("LY-218","Libya (+218)")
,("LI-417","Liechtenstein (+417)")
,("LT-370","Lithuania (+370)")
,("LU-352","Luxembourg (+352)")
,("MO-853","Macao (+853)")
,("MK-389","Macedonia (+389)")
,("MG-261","Madagascar (+261)")
,("MW-265","Malawi (+265)")
,("MY-60","Malaysia (+60)")
,("MV-960","Maldives (+960)")
,("ML-223","Mali (+223)")
,("MT-356","Malta (+356)")
,("MH-692","Marshall Islands (+692)")
,("MQ-596","Martinique (+596)")
,("MR-222","Mauritania (+222)")
,("YT-269","Mayotte (+269)")
,("MX-52","Mexico (+52)")
,("FM-691","Micronesia (+691)")
,("MD-373","Moldova (+373)")
,("MC-377","Monaco (+377)")
,("MN-976","Mongolia (+976)")
,("MS-1664","Montserrat (+1664)")
,("MA-212","Morocco (+212)")
,("MZ-258","Mozambique (+258)")
,("MN-95","Myanmar (+95)")
,("NA-264","Namibia (+264)")
,("NR-674","Nauru (+674)")
,("NP-977","Nepal (+977)")
,("NL-31","Netherlands (+31)")
,("NC-687","New Caledonia (+687)")
,("NZ-64","New Zealand (+64)")
,("NI-505","Nicaragua (+505)")
,("NE-227","Niger (+227)")
,("NG-234","Nigeria (+234)")
,("NU-683","Niue (+683)")
,("NF-672","Norfolk Islands (+672)")
,("NP-670","Northern Marianas (+670)")
,("NO-47","Norway (+47)")
,("OM-968","Oman (+968)")
,("PW-680","Palau (+680)")
,("PA-507","Panama (+507)")
,("PG-675","Papua New Guinea (+675)")
,("PY-595","Paraguay (+595)")
,("PE-51","Peru (+51)")
,("PH-63","Philippines (+63)")
,("PL-48","Poland (+48)")
,("PT-351","Portugal (+351)")
,("PR-1787","Puerto Rico (+1787)")
,("QA-974","Qatar (+974)")
,("RE-262","Reunion (+262)")
,("RO-40","Romania (+40)")
,("RU-7","Russia (+7)")
,("RW-250","Rwanda (+250)")
,("SM-378","San Marino (+378)")
,("ST-239","Sao Tome &amp; Principe (+239)")
,("SA-966","Saudi Arabia (+966)")
,("SN-221","Senegal (+221)")
,("CS-381","Serbia (+381)")
,("SC-248","Seychelles (+248)")
,("SL-232","Sierra Leone (+232)")
,("SG-65","Singapore (+65)")
,("SK-421","Slovak Republic (+421)")
,("SI-386","Slovenia (+386)")
,("SB-677","Solomon Islands (+677)")
,("SO-252","Somalia (+252)")
,("ZA-27","South Africa (+27)")
,("ES-34","Spain (+34)")
,("LK-94","Sri Lanka (+94)")
,("SH-290","St. Helena (+290)")
,("KN-1869","St. Kitts (+1869)")
,("SC-1758","St. Lucia (+1758)")
,("SD-249","Sudan (+249)")
,("SR-597","Suriname (+597)")
,("SZ-268","Swaziland (+268)")
,("SE-46","Sweden (+46)")
,("CH-41","Switzerland (+41)")
,("SI-963","Syria (+963)")
,("TW-886","Taiwan (+886)")
,("TJ-7","Tajikstan (+7)")
,("TH-66","Thailand (+66)")
,("TG-228","Togo (+228)")
,("TO-676","Tonga (+676)")
,("TT-1868","Trinidad &amp; Tobago (+1868)")
,("TN-216","Tunisia (+216)")
,("TR-90","Turkey (+90)")
,("TM-7","Turkmenistan (+7)")
,("TM-993","Turkmenistan (+993)")
,("TC-1649","Turks &amp; Caicos Islands (+1649)")
,("TV-688","Tuvalu (+688)")
,("UG-256","Uganda (+256)")
,("GB-44","UK (+44)")
,("UA-380","Ukraine (+380)")
,("AE-971","United Arab Emirates (+971)")
,("UY-598","Uruguay (+598)")
,("US-1","USA (+1)")
,("UZ-7","Uzbekistan (+7)")
,("VU-678","Vanuatu (+678)")
,("VA-379","Vatican City (+379)")
,("VE-58","Venezuela (+58)")
,("VN-84","Vietnam (+84)")
,("VG-84","Virgin Islands - British (+1284)")
,("VI-84","Virgin Islands - US (+1340)")
,("WF-681","Wallis &amp; Futuna (+681)")
,("YE-969","Yemen (North)(+969)")
,("YE-967","Yemen (South)(+967)")
,("ZM-260","Zambia (+260)")
,("ZW-263","Zimbabwe (+263)"))

status_types = (
    ('select', 'Select Status'),
    ('active', 'Active'),
    ('closed', 'Inactive'),
    )

UNAME_CHARS = letters + "._" + digits
PWD_CHARS = letters + punctuation + digits

attempts = [(i, i) for i in range(1, 6)]
attempts.append((-1, 'Infinite'))
days_between_attempts = ((j, j) for j in range(401))

# Add bootstrap class separated by space
form_input_class = "form-control"


def get_object_form(model, exclude_fields=None):
    model_class = get_model_class(model)

    class _ObjectForm(forms.ModelForm):
        class Meta:
            model = model_class
            exclude = exclude_fields
    return _ObjectForm


class UserRegisterForm(forms.Form):
    """A Class to create new form for User's Registration.
    It has the various fields and functions required to register
    a new user to the system"""

    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            {'class': form_input_class, 'placeholder': "Username : Letters, digits, period and underscores only."})
        )
    email = forms.EmailField(widget=forms.TextInput(
        {'class': form_input_class, 'placeholder': "Email"}
        ))
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(
            {'class': form_input_class, 'placeholder': "Password"}))
    confirm_password = forms.CharField(
        max_length=30, widget=forms.PasswordInput(
            {'class': form_input_class, 'placeholder': "Confirm Password"}
            ))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        {'class': form_input_class, 'placeholder': "First Name"}
        ))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
        {'class': form_input_class, 'placeholder': "Last Name"}
        ))
    country_code = forms.ChoiceField(choices=country_codes, initial="IN-91", required = True, widget=forms.Select(attrs={"class": "form-control", 'placeholder': "country code"}))
    phone_number = forms.CharField(max_length=10, widget=forms.TextInput(
        {'class': form_input_class, 'placeholder': "Phone Number"}
        ))
    # roll_number = forms.CharField(
    #     max_length=30, help_text="Use a dummy if you don't have one.",
    #     widget=forms.TextInput(
    #         {'class': form_input_class, 'placeholder': "Roll Number"}
    #     ))
    # institute = forms.CharField(
    #     max_length=128, help_text='Institute/Organization',
    #     widget=forms.TextInput(
    #         {'class': form_input_class, 'placeholder': "Institute"}
    #     ))
    # department = forms.CharField(
    #     max_length=64, help_text='Department you work/study at',
    #     widget=forms.TextInput(
    #         {'class': form_input_class, 'placeholder': "Department"}
    #     ))
    # position = forms.CharField(
    #     max_length=64,
    #     help_text='Student/Faculty/Researcher/Industry/Fellowship/etc.',
    #     widget=forms.TextInput(
    #         {'class': form_input_class, 'placeholder': "Position"}
    #     ))
    # timezone = forms.ChoiceField(
    #     choices=[(tz, tz) for tz in pytz.common_timezones],
    #     help_text='All timings are shown based on the selected timezone',
    #     widget=forms.Select({'class': 'custom-select'}),
    #     initial=pytz.country_timezones['IN'][0])

    def clean_username(self):
        u_name = self.cleaned_data["username"]
        if u_name.strip(UNAME_CHARS):
            msg = "Only letters, digits, period and underscore characters are"\
                  " allowed in username"
            raise forms.ValidationError(msg)
        try:
            User.objects.get(username__exact=u_name)
            raise forms.ValidationError("Username already exists.")
        except User.DoesNotExist:
            return u_name

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if pwd.strip(PWD_CHARS):
            raise forms.ValidationError("Only letters, digits and punctuation\
                                        are allowed in password")
        return pwd

    def clean_confirm_password(self):
        c_pwd = self.cleaned_data['confirm_password']
        pwd = self.data['password']
        if c_pwd != pwd:
            raise forms.ValidationError("Passwords do not match")

        return c_pwd

    def clean_email(self):
        user_email = self.cleaned_data['email']
        if User.objects.filter(email=user_email).exists():
            raise forms.ValidationError("This email already exists")
        return user_email

    def clean_phone_number(self):
        user_phone_number = self.cleaned_data['phone_number']
        if Profile.objects.filter(phone_number=user_phone_number).exists():
            raise forms.ValidationError("This phone number already exists")
        return user_phone_number

    def clean_country_code(self):
        user_country_code = self.cleaned_data['country_code']
        user_country_code = '+' + user_country_code.split('-')[1]
        return user_country_code

    def save(self):
        u_name = self.cleaned_data["username"]
        u_name = u_name.lower()
        pwd = self.cleaned_data["password"]
        email = self.cleaned_data['email']
        country_code = self.cleaned_data['country_code']
        phone_number = self.cleaned_data['phone_number']
        new_user = User.objects.create_user(u_name, email, pwd)

        new_user.first_name = self.cleaned_data["first_name"]
        new_user.last_name = self.cleaned_data["last_name"]
        new_user.save()

        new_profile = Profile(user=new_user)
        new_profile.country_code = country_code
        new_profile.phone_number = phone_number

        if settings.IS_DEVELOPMENT:
            new_profile.is_email_verified = True
        else:
            new_profile.is_email_verified = True
            new_profile.activation_key = generate_activation_key(
                new_user.username)
            new_profile.key_expiry_time = timezone.now() + timezone.timedelta(
                minutes=20)
        new_profile.save()
        return u_name, pwd, new_user.email, new_profile.activation_key


class UserLoginForm(forms.Form):
    """Creates a form which will allow the user to log into the system."""

    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': form_input_class, 'placeholder': 'Username'}
        )
    )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(
            attrs={'class': form_input_class, 'placeholder': 'Password'}
        )
    )

    def clean(self):
        super(UserLoginForm, self).clean()
        try:
            u_name, pwd = self.cleaned_data["username"],\
                          self.cleaned_data["password"]
            user = authenticate(username=u_name, password=pwd)
        except Exception:
            raise forms.ValidationError(
                "Username and/or Password is not entered"
            )
        if not user:
            raise forms.ValidationError("Invalid username/password")
        return user


class ExerciseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExerciseForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': "Exercise Description"}
        )

    class Meta:
        model = Quiz
        fields = ['description', 'view_answerpaper', 'active']


class QuizForm(forms.ModelForm):
    """Creates a form to add or edit a Quiz.
    It has the related fields and functions required."""

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)

        self.fields['start_date_time'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['end_date_time'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['duration'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['description'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['attempts_allowed'].widget.attrs.update(
            {'class': 'custom-select'}
        )
        self.fields['time_between_attempts'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['instructions'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['weightage'].widget.attrs.update(
            {'class': form_input_class}
        )
        self.fields['pass_criteria'].widget.attrs.update(
            {'class': form_input_class}
        )

        self.fields["instructions"].initial = dedent("""\
            <p>
            This examination system has been developed with the intention of
            making you learn programming and be assessed in an interactive and
            fun manner.You will be presented with a series of programming
            questions and problems that you will answer online and get
            immediate feedback for.
            </p><p>Here are some important instructions and rules that you
            should understand carefully.</p>
            <ul><li>For any programming questions, you can submit solutions as
            many times as you want without a penalty. You may skip questions
            and solve them later.</li><li> You <strong>may</strong>
            use your computer's Python/IPython shell or an editor to solve the
            problem and cut/paste the solution to the web interface.
            </li><li> <strong>You are not allowed to use any internet resources
            i.e. no google etc.</strong>
            </li>
            <li> Do not copy or share the questions or answers with anyone
            until the exam is complete <strong>for everyone</strong>.
            </li><li> <strong>All</strong> your attempts at the questions are
            logged. Do not try to outsmart and break the testing system.
            If you do, we know who you are and we will expel you from the
            course. You have been warned.
            </li></ul>
            <p>We hope you enjoy taking this exam !!!</p>
        """)

    class Meta:
        model = Quiz
        exclude = ["is_trial", "creator", "is_exercise"]


class QuestionForm(forms.ModelForm):
    """Creates a form to add or edit a Question.
    It has the related fields and functions required."""

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['summary'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Summary'}
        )
        self.fields['language'].widget.attrs.update(
            {'class': 'custom-select'}
        )
        self.fields['topic'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Topic name'}
        )
        self.fields['type'].widget.attrs.update(
            {'class': 'custom-select'}
        )
        self.fields['description'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Description'}
        )
        self.fields['tags'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Tags'}
        )
        self.fields['solution'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Solution'}
        )
        self.fields['snippet'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Snippet'}
        )
        self.fields['min_time'].widget.attrs.update(
            {'class': form_input_class}
        )

    class Meta:
        model = Question
        exclude = ['user', 'active']


class FileForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(
                                attrs={
                                    'multiple': True,
                                    'class': 'custom-file-input'
                                    }
                                ),
                                required=False)


class RandomQuestionForm(forms.Form):
    question_type = forms.CharField(
        max_length=8, widget=forms.Select(choices=question_types)
    )
    marks = forms.CharField(
        max_length=8, widget=forms.Select(
            choices=(('select', 'Select Marks'),))
    )
    shuffle_questions = forms.BooleanField(required=False)


class QuestionFilterForm(forms.Form):

    language = forms.ChoiceField(
        choices=languages,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=False
        )
    question_type = forms.ChoiceField(
        choices=question_types,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        lang = kwargs.pop("language") if "language" in kwargs else None
        que_type = kwargs.pop("type") if "type" in kwargs else None
        marks = kwargs.pop("marks") if "marks" in kwargs else None
        super(QuestionFilterForm, self).__init__(*args, **kwargs)
        points = Question.objects.filter(
            user_id=user.id).values_list('points', flat=True).distinct()
        points_options = [('', 'Select Marks')]
        points_options.extend([(point, point) for point in points])
        self.fields['marks'] = forms.ChoiceField(
            choices=points_options,
            widget=forms.Select(attrs={'class': 'custom-select'}),
            required=False
        )
        self.fields['marks'].required = False
        self.fields['language'].initial = lang
        self.fields['question_type'].initial = que_type
        self.fields['marks'].initial = marks


class SearchFilterForm(forms.Form):
    search_tags = forms.CharField(
        label='Search Tags',
        widget=forms.TextInput(attrs={'placeholder': 'Search',
                                      'class': form_input_class, }),
        required=False
        )
    search_status = forms.ChoiceField(
        choices=status_types,
        widget=forms.Select(attrs={'class': 'custom-select'})
        )

    def __init__(self, *args, **kwargs):
        status = kwargs.pop("status") if "status" in kwargs else None
        tags = kwargs.pop("tags") if "tags" in kwargs else None
        super(SearchFilterForm, self).__init__(*args, **kwargs)
        self.fields["search_status"].initial = status
        self.fields["search_tags"].initial = tags


class CourseForm(forms.ModelForm):
    """ course form for moderators """
    class Meta:
        model = Course
        fields = [
            'name', 'enrollment', 'active', 'code', 'instructions',
            'start_enroll_time', 'end_enroll_time', 'grading_system',
            'view_grade'
        ]

    def save(self, commit=True, *args, **kwargs):
        instance = super(CourseForm, self).save(commit=False)
        if instance.code:
            instance.hidden = True
        else:
            instance.hidden = False

        if commit:
            instance.save()
        return instance

    def __init__(self, user, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Course Name'}
        )
        self.fields['enrollment'].widget.attrs.update(
            {'class': 'custom-select'}
        )
        self.fields['code'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Course Code'}
        )
        self.fields['instructions'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Course instructions'}
        )
        self.fields['start_enroll_time'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Course Start DateTime'}
        )
        self.fields['end_enroll_time'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Course End DateTime'}
        )
        self.fields['grading_system'].widget.attrs.update(
            {'class': 'custom-select'}
        )
        if (self.instance.id and
                self.instance.teachers.filter(id=user.id).exists()):
            self.fields['grading_system'].widget.attrs['disabled'] = True
        else:
            grading_choices = GradingSystem.objects.filter(
                creator=user
            )
            self.fields['grading_system'].queryset = grading_choices


class ProfileForm(forms.ModelForm):
    """ profile form for students and moderators """

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name']

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
                    {'class': form_input_class, 'placeholder': "First Name"}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
                    {'class': form_input_class, 'placeholder': "Last Name"}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['first_name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'First Name'}
        )
        self.fields['last_name'].initial = user.last_name
        self.fields['last_name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Last Name'}
        )
        # self.fields['institute'].widget.attrs.update(
        #     {'class': form_input_class, 'placeholder': 'Institute'}
        # )
        # self.fields['department'].widget.attrs.update(
        #     {'class': form_input_class, 'placeholder': 'Department'}
        # )
        # self.fields['roll_number'].widget.attrs.update(
        #     {'class': form_input_class, 'placeholder': 'Roll Number'}
        # )
        # self.fields['position'].widget.attrs.update(
        #     {'class': form_input_class, 'placeholder': 'Position'}
        # )
        # self.fields['timezone'] = forms.ChoiceField(
        #     choices=[(tz, tz) for tz in pytz.common_timezones],
        #     help_text='All timings are shown based on the selected timezone',
        #     widget=forms.Select({'class': 'custom-select'})
        #     )


class UploadFileForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'custom-file-input'})
    )


class QuestionPaperForm(forms.ModelForm):
    class Meta:
        model = QuestionPaper
        fields = ['shuffle_questions', 'shuffle_testcases']


class LessonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)
        des_msg = "Enter Lesson Description as Markdown text"
        self.fields['name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Lesson Name'}
        )
        self.fields['description'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': des_msg}
        )
        self.fields['video_file'].widget.attrs.update(
            {'class': "custom-file-input"}
        )

    class Meta:
        model = Lesson
        exclude = ['creator', 'html_data']

    def clean_video_file(self):
        file = self.cleaned_data.get("video_file")
        if file:
            extension = file.name.split(".")[-1]
            actual_extension = ["mp4", "ogv", "webm"]
            if extension not in actual_extension:
                raise forms.ValidationError(
                    "Please upload video files in {0} format".format(
                        ", ".join(actual_extension))
                    )
        return file


class LessonFileForm(forms.Form):
    Lesson_files = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'class': "custom-file-input"}),
        required=False)


class LearningModuleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LearningModuleForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['size'] = 30
        self.fields['name'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Module Name'}
        )
        self.fields['description'].widget.attrs.update(
            {'class': form_input_class, 'placeholder': 'Module Description'}
        )

    class Meta:
        model = LearningModule
        fields = ['name', 'description', 'active']


class TestcaseForm(forms.ModelForm):

    type = forms.CharField(
        widget=forms.TextInput(
            attrs={'readonly': 'readonly', 'class': form_input_class})
    )

    class Meta:
        model = TestCase
        fields = ["type"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "image"]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'form-control-file'
                }
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["description", "image"]
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'form-control-file'
                }
            )
        }
