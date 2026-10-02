<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* database/qbe/selection_form.twig */
class __TwigTemplate_5c363a5df1da1b47f612cf68406f56c4f5fef252e5ade336e97ca3307b95914c extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 1
        echo "<form action=\"";
        echo PhpMyAdmin\Url::getFromRoute("/database/qbe");
        echo "\" method=\"post\" id=\"formQBE\" class=\"lock-page\">
  ";
        // line 2
        echo PhpMyAdmin\Url::getHiddenInputs(($context["url_params"] ?? null));
        echo "

  <div class=\"w-100\">
    <fieldset>

      ";
        // line 7
        echo ($context["saved_searches_field"] ?? null);
        echo "

      <div class=\"table-responsive jsresponsive\">
        <table class=\"table table-borderless table-sm\">
          <tr class=\"noclick\">
            <th>";
        // line 12
        echo _gettext("Column:");
        echo "</th>
            ";
        // line 13
        echo ($context["column_names_row"] ?? null);
        echo "
          </tr>

          <tr class=\"noclick\">
            <th>";
        // line 17
        echo _gettext("Alias:");
        echo "</th>
            ";
        // line 18
        echo ($context["column_alias_row"] ?? null);
        echo "
          </tr>

          <tr class=\"noclick\">
            <th>";
        // line 22
        echo _gettext("Show:");
        echo "</th>
            ";
        // line 23
        echo ($context["show_row"] ?? null);
        echo "
          </tr>

          <tr class=\"noclick\">
            <th>";
        // line 27
        echo _gettext("Sort:");
        echo "</th>
            ";
        // line 28
        echo ($context["sort_row"] ?? null);
        echo "
          </tr>

          <tr class=\"noclick\">
            <th>";
        // line 32
        echo _gettext("Sort order:");
        echo "</th>
            ";
        // line 33
        echo ($context["sort_order"] ?? null);
        echo "
          </tr>

          <tr class=\"noclick\">
            <th>";
        // line 37
        echo _gettext("Criteria:");
        echo "</th>
            ";
        // line 38
        echo ($context["criteria_input_box_row"] ?? null);
        echo "
          </tr>

          ";
        // line 41
        echo ($context["ins_del_and_or_criteria_rows"] ?? null);
        echo "

          <tr class=\"noclick\">
            <th>";
        // line 44
        echo _gettext("Modify:");
        echo "</th>
            ";
        // line 45
        echo ($context["modify_columns_row"] ?? null);
        echo "
          </tr>
        </table>
      </div>
    </fieldset>
  </div>

  <fieldset class=\"tblFooters\">
    <div class=\"floatleft\">
      <label for=\"criteriaRowAddSelect\">";
        // line 54
        echo _gettext("Add/Delete criteria rows:");
        echo "</label>
      <select size=\"1\" name=\"criteriaRowAdd\" id=\"criteriaRowAddSelect\">
        <option value=\"-3\">-3</option>
        <option value=\"-2\">-2</option>
        <option value=\"-1\">-1</option>
        <option value=\"0\" selected>0</option>
        <option value=\"1\">1</option>
        <option value=\"2\">2</option>
        <option value=\"3\">3</option>
      </select>
    </div>

    <div class=\"floatleft\">
      <label for=\"criteriaColumnAddSelect\">";
        // line 67
        echo _gettext("Add/Delete columns:");
        echo "</label>
      <select size=\"1\" name=\"criteriaColumnAdd\" id=\"criteriaColumnAddSelect\">
        <option value=\"-3\">-3</option>
        <option value=\"-2\">-2</option>
        <option value=\"-1\">-1</option>
        <option value=\"0\" selected>0</option>
        <option value=\"1\">1</option>
        <option value=\"2\">2</option>
        <option value=\"3\">3</option>
      </select>
    </div>

    <div class=\"floatleft\">
      <input class=\"btn btn-secondary\" type=\"submit\" name=\"modify\" value=\"";
        // line 80
        echo _gettext("Update query");
        echo "\">
    </div>
  </fieldset>

  <div class=\"floatleft w-100\">
    <fieldset>
      <legend>";
        // line 86
        echo _gettext("Use tables");
        echo "</legend>

      <select name=\"TableList[]\" id=\"listTable\" size=\"";
        // line 88
        echo (((twig_length_filter($this->env, ($context["criteria_tables"] ?? null)) > 30)) ? ("15") : ("7"));
        echo "\" aria-label=\"";
        echo _gettext("Use tables");
        echo "\" multiple>
        ";
        // line 89
        $context['_parent'] = $context;
        $context['_seq'] = twig_ensure_traversable(($context["criteria_tables"] ?? null));
        foreach ($context['_seq'] as $context["table"] => $context["selected"]) {
            // line 90
            echo "          <option value=\"";
            echo twig_escape_filter($this->env, $context["table"], "html", null, true);
            echo "\"";
            echo $context["selected"];
            echo ">";
            echo twig_escape_filter($this->env, $context["table"], "html", null, true);
            echo "</option>
        ";
        }
        $_parent = $context['_parent'];
        unset($context['_seq'], $context['_iterated'], $context['table'], $context['selected'], $context['_parent'], $context['loop']);
        $context = array_intersect_key($context, $_parent) + $_parent;
        // line 92
        echo "      </select>
    </fieldset>

    <fieldset class=\"tblFooters\">
      <input class=\"btn btn-secondary\" type=\"submit\" name=\"modify\" value=\"";
        // line 96
        echo _gettext("Update query");
        echo "\">
    </fieldset>
  </div>
</form>

<form action=\"";
        // line 101
        echo PhpMyAdmin\Url::getFromRoute("/database/qbe");
        echo "\" method=\"post\" class=\"lock-page\">
  ";
        // line 102
        echo PhpMyAdmin\Url::getHiddenInputs(($context["db"] ?? null));
        echo "
  <input type=\"hidden\" name=\"submit_sql\" value=\"1\">

  <div class=\"floatleft w-50\">
    <fieldset id=\"tblQbe\">
      <legend>";
        // line 107
        echo sprintf(_gettext("SQL query on database <b>%s</b>:"), ($context["db_link"] ?? null));
        echo "</legend>

      <textarea cols=\"80\" name=\"sql_query\" id=\"textSqlquery\" rows=\"";
        // line 109
        echo (((twig_length_filter($this->env, ($context["criteria_tables"] ?? null)) > 30)) ? ("15") : ("7"));
        echo "\" dir=\"ltr\" aria-label=\"";
        echo _gettext("SQL query");
        echo "\">";
        // line 110
        echo twig_escape_filter($this->env, ($context["sql_query"] ?? null), "html", null, true);
        // line 111
        echo "</textarea>
    </fieldset>

    <fieldset class=\"tblFooters\" id=\"tblQbeFooters\">
      <input class=\"btn btn-primary\" type=\"submit\" value=\"";
        // line 115
        echo _gettext("Submit query");
        echo "\">
    </fieldset>
  </div>
</form>
";
    }

    public function getTemplateName()
    {
        return "database/qbe/selection_form.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  258 => 115,  252 => 111,  250 => 110,  245 => 109,  240 => 107,  232 => 102,  228 => 101,  220 => 96,  214 => 92,  201 => 90,  197 => 89,  191 => 88,  186 => 86,  177 => 80,  161 => 67,  145 => 54,  133 => 45,  129 => 44,  123 => 41,  117 => 38,  113 => 37,  106 => 33,  102 => 32,  95 => 28,  91 => 27,  84 => 23,  80 => 22,  73 => 18,  69 => 17,  62 => 13,  58 => 12,  50 => 7,  42 => 2,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "database/qbe/selection_form.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\database\\qbe\\selection_form.twig");
    }
}
