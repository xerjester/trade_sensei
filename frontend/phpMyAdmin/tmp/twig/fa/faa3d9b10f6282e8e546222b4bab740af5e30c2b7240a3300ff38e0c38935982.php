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

/* database/triggers/row.twig */
class __TwigTemplate_d332f3521f7fe4f27e5c94f9b9b931534178096eeb94e63183094d2c5c14dde0 extends \Twig\Template
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
        echo "<tr";
        if ( !twig_test_empty(($context["row_class"] ?? null))) {
            echo " class=\"";
            echo twig_escape_filter($this->env, ($context["row_class"] ?? null), "html", null, true);
            echo "\"";
        }
        echo ">
  <td>
    <input type=\"checkbox\" class=\"checkall\" name=\"item_name[]\" value=\"";
        // line 3
        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "name", [], "any", false, false, false, 3), "html", null, true);
        echo "\">
  </td>
  <td>
    <span class='drop_sql hide'>";
        // line 6
        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "drop", [], "any", false, false, false, 6), "html", null, true);
        echo "</span>
    <strong>";
        // line 7
        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "name", [], "any", false, false, false, 7), "html", null, true);
        echo "</strong>
  </td>
  ";
        // line 9
        if (twig_test_empty(($context["table"] ?? null))) {
            // line 10
            echo "    <td>
      <a href=\"";
            // line 11
            echo PhpMyAdmin\Url::getFromRoute("/table/triggers", ["db" => ($context["db"] ?? null), "table" => twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "table", [], "any", false, false, false, 11)]);
            echo "\">";
            echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "table", [], "any", false, false, false, 11), "html", null, true);
            echo "</a>
    </td>
  ";
        }
        // line 14
        echo "  <td>
    ";
        // line 15
        if (($context["has_edit_privilege"] ?? null)) {
            // line 16
            echo "      <a class=\"ajax edit_anchor\" href=\"";
            echo PhpMyAdmin\Url::getFromRoute("/database/triggers", ["db" =>             // line 17
($context["db"] ?? null), "table" =>             // line 18
($context["table"] ?? null), "edit_item" => true, "item_name" => twig_get_attribute($this->env, $this->source,             // line 20
($context["trigger"] ?? null), "name", [], "any", false, false, false, 20)]);
            // line 21
            echo "\">
        ";
            // line 22
            echo \PhpMyAdmin\Html\Generator::getIcon("b_edit", _gettext("Edit"));
            echo "
      </a>
    ";
        } else {
            // line 25
            echo "      ";
            echo \PhpMyAdmin\Html\Generator::getIcon("bd_edit", _gettext("Edit"));
            echo "
    ";
        }
        // line 27
        echo "  </td>
  <td>
    <a class=\"ajax export_anchor\" href=\"";
        // line 29
        echo PhpMyAdmin\Url::getFromRoute("/database/triggers", ["db" =>         // line 30
($context["db"] ?? null), "table" =>         // line 31
($context["table"] ?? null), "export_item" => true, "item_name" => twig_get_attribute($this->env, $this->source,         // line 33
($context["trigger"] ?? null), "name", [], "any", false, false, false, 33)]);
        // line 34
        echo "\">
      ";
        // line 35
        echo \PhpMyAdmin\Html\Generator::getIcon("b_export", _gettext("Export"));
        echo "
    </a>
  </td>
  <td>
    ";
        // line 39
        if (($context["has_drop_privilege"] ?? null)) {
            // line 40
            echo "      ";
            echo PhpMyAdmin\Html\Generator::linkOrButton(PhpMyAdmin\Url::getFromRoute("/sql", ["db" =>             // line 42
($context["db"] ?? null), "table" =>             // line 43
($context["table"] ?? null), "sql_query" => twig_get_attribute($this->env, $this->source,             // line 44
($context["trigger"] ?? null), "drop", [], "any", false, false, false, 44), "goto" => PhpMyAdmin\Url::getFromRoute("/database/triggers", ["db" =>             // line 45
($context["db"] ?? null)])]), \PhpMyAdmin\Html\Generator::getIcon("b_drop", _gettext("Drop")), ["class" => "ajax drop_anchor"]);
            // line 49
            echo "
    ";
        } else {
            // line 51
            echo "      ";
            echo \PhpMyAdmin\Html\Generator::getIcon("bd_drop", _gettext("Drop"));
            echo "
    ";
        }
        // line 53
        echo "  </td>
  <td>
    ";
        // line 55
        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "action_timing", [], "any", false, false, false, 55), "html", null, true);
        echo "
  </td>
  <td>
    ";
        // line 58
        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["trigger"] ?? null), "event_manipulation", [], "any", false, false, false, 58), "html", null, true);
        echo "
  </td>
</tr>
";
    }

    public function getTemplateName()
    {
        return "database/triggers/row.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  149 => 58,  143 => 55,  139 => 53,  133 => 51,  129 => 49,  127 => 45,  126 => 44,  125 => 43,  124 => 42,  122 => 40,  120 => 39,  113 => 35,  110 => 34,  108 => 33,  107 => 31,  106 => 30,  105 => 29,  101 => 27,  95 => 25,  89 => 22,  86 => 21,  84 => 20,  83 => 18,  82 => 17,  80 => 16,  78 => 15,  75 => 14,  67 => 11,  64 => 10,  62 => 9,  57 => 7,  53 => 6,  47 => 3,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "database/triggers/row.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\database\\triggers\\row.twig");
    }
}
